import asyncio
import time
from datetime import datetime

import aiocron

import api.chatgpt
from api.middlewares import AccessLoggerMiddleware, StatisticsMiddleware
from httpx import HTTPError
import uvicorn

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from sqlalchemy import select, update
from starlette.exceptions import HTTPException as StarletteHTTPException

import api.globals as g
import os
from utils import chatgpt_user_helper
import utils.store_statistics
from utils.sync_conversations import sync_conversations

from api.enums import ChatStatus, PlanLevel
from api.models import ChatGPTUser, Conversation, User
from api.response import CustomJSONResponse, PrettyJSONResponse, handle_exception_response
from api.database import create_db_and_tables, get_async_session_context
from api.exceptions import SelfDefinedException
from api.routers import users, chat, system, status
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware

from utils.logger import setup_logger, get_log_config, get_logger
from utils.proxy import close_reverse_proxy
from utils.create_user import create_user

import dateutil.parser
from revChatGPT.typings import Error as revChatGPTError

config = g.config

setup_logger()

logger = get_logger(__name__)

app = FastAPI(
    default_response_class=CustomJSONResponse,
    middleware=[
        Middleware(AccessLoggerMiddleware, format='%(client_addr)s | %(request_line)s | %(status_code)s | %(M)s ms',
                   logger=get_logger("access")),
        Middleware(StatisticsMiddleware)]
)

app.include_router(users.router)
app.include_router(chat.router)
app.include_router(system.router)
app.include_router(status.router)

origins = [
    "http://localhost",
    "http://localhost:4000",
]

# 解决跨站问题
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 定义若干异常处理器


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return handle_exception_response(exc)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return handle_exception_response(exc)


@app.exception_handler(SelfDefinedException)
async def validation_exception_handler(request, exc):
    return handle_exception_response(exc)


@app.exception_handler(revChatGPTError)
async def validation_exception_handler(request, exc):
    return handle_exception_response(exc)


@app.on_event("startup")
async def on_startup():
    await create_db_and_tables()
    logger.info("database initialized")
    g.startup_time = time.time()

    utils.store_statistics.load()

    if config.get("create_initial_admin_user", False):
        await create_user(config.get("initial_admin_username"),
                          "admin",
                          "admin@admin.com",
                          config.get("initial_admin_password"),
                          is_superuser=True)

    if config.get("create_initial_user", False):
        await create_user(config.get("initial_user_username"),
                          "user",
                          "user@user.com",
                          config.get("initial_user_password"),
                          is_superuser=False)

    if not config.get("sync_conversations_on_startup", True):
        return

    # 重置所有用户chat_status
    async with get_async_session_context() as session:
        r = await session.execute(select(User))
        results = r.scalars().all()
        for user in results:
            user.chat_status = ChatStatus.idling
            session.add(user)
        await session.commit()

    chatgpt_users: list[ChatGPTUser] = []
    # 初始化 chatgpt_managers
    async with get_async_session_context() as session:
        r = await session.execute(select(ChatGPTUser).where(ChatGPTUser.is_active))
        chatgpt_users = r.scalars().all()
        for chatgpt_user in chatgpt_users:
            if chatgpt_user.is_active:
                try:
                    logger.info(f"Initializing chatgpt_manager for {chatgpt_user.email}")
                    password = None
                    if chatgpt_user.hashed_password:
                        password = chatgpt_user_helper.decrypt(chatgpt_user.hashed_password)
                    elif not chatgpt_user.access_token:
                        logger.warn(f"chatgpt_user {chatgpt_user.email} has no password or access_token")
                        continue

                    chatgpt_manager = api.chatgpt.ChatGPTManager({
                        "email": chatgpt_user.email,
                        "password": password,
                        "access_token": chatgpt_user.access_token,
                        "session_token": chatgpt_user.session_token,
                        "paid": chatgpt_user.is_plus
                    })
                    g.chatgpt_managers[chatgpt_user.id] = chatgpt_manager
                    logger.info(f"chatgpt_manager for {chatgpt_user.email} initialized")
                except Exception as e:
                    logger.error(f"Error when initializing chatgpt_manager for {chatgpt_user.email}: {e}")
    g.chatgpt_users = chatgpt_users
    logger.info("All chatgpt_managers initialized")

    # 定时刷新 access_token 和 puid
    # 每 6 天刷新一次
    @aiocron.crontab('0 0 */6 * *', loop=asyncio.get_event_loop())
    async def refresh_access_token():
        logger.info("Refreshing access_token and puid...")
        for chatgpt_user in chatgpt_users:
            try:
                # refresh access token
                chatgpt_manager = g.chatgpt_managers[chatgpt_user.id]
                chatgpt_manager.chatbot.login()
                logger.info(f"{chatgpt_user.email} login success.")

                access_token = chatgpt_manager.chatbot.config["access_token"]
                is_access_token_updated = access_token != chatgpt_user.access_token
                logger.info(f"Is access_token updated? {is_access_token_updated}")
                session_token = chatgpt_manager.chatbot.config["session_token"]
                is_session_token_updated = session_token != chatgpt_user.session_token
                logger.info(f"Is session_token updated? {is_session_token_updated}")
                if chatgpt_user.is_plus:
                    from utils.proxy import refresh_puid
                    puid = refresh_puid(chatgpt_user.email, access_token, chatgpt_user.puid)
                    is_puid_updated = puid != chatgpt_user.puid
                    logger.info(f"{chatgpt_user.email} puid refreshed. Is puid updated? {is_puid_updated}")
                    if is_puid_updated:
                        chatgpt_user.puid = puid
                        chatgpt_user.puid_refresh_time = datetime.now()
                if is_access_token_updated:
                    chatgpt_user.access_token = access_token
                    chatgpt_user.access_token_refresh_time = datetime.now()
                if is_session_token_updated:
                    chatgpt_user.session_token = session_token
                    chatgpt_user.session_token_refresh_time = datetime.now()

                if is_access_token_updated or is_session_token_updated or is_puid_updated:
                    async with get_async_session_context() as session:
                        session.add(chatgpt_user)
                        await session.commit()
            except Exception as e:
                logger.error(f"Error when refreshing access_token for {chatgpt_user.email}: {e}")
            time.sleep(5)
        logger.info("All access_token refreshed")

    # 运行 Proxy Server
    if config.get("run_reverse_proxy", False):
        from utils.proxy import run_reverse_proxy
        run_reverse_proxy(chatgpt_users)
        await asyncio.sleep(2)  # 等待 Proxy Server 启动

    logger.info(f"Using {os.environ.get('CHATGPT_BASE_URL', '<default_bypass>')} as ChatGPT base url")

    # 获取 ChatGPT 对话，并同步数据库
    if not config.get("sync_conversations_on_startup", True):
        logger.info("Sync conversations on startup disabled. Jumping...")
        return  # 跳过同步对话
    else:
        await sync_conversations()

    @aiocron.crontab('*/5 * * * *', loop=asyncio.get_event_loop())
    async def dump_stats():
        utils.store_statistics.dump(print_log=False)

    if config.get("sync_conversations_regularly", True):
        logger.info("Sync conversations regularly enabled, will sync conversations every 12 hours.")

        # 默认每隔 12 小时同步一次
        @aiocron.crontab('0 */12 * * *', loop=asyncio.get_event_loop())
        async def sync_conversations_regularly():
            await sync_conversations()

    # 每日 2 点重置basic套餐用户的可提问次数
    @aiocron.crontab('0 2 * * *', loop=asyncio.get_event_loop())
    async def reset_basic_users_available_ask_count():
        logger.info("Resetting basic user's available ask count...")
        async with get_async_session_context() as session:
            await session.execute(
                update(User)
                .where(User.plan_level == PlanLevel.basic and User.is_verified and User.is_active)
                .values(available_ask_count=10)
            )
            await session.commit()
        logger.info("Basic user's available ask count reset.")

# 关闭时
@app.on_event("shutdown")
async def on_shutdown():
    logger.info("On shutdown...")
    close_reverse_proxy()
    utils.store_statistics.dump()


# @api.get("/routes")
# async def root():
#     url_list = [{"name": route.name, "path": route.path, "path_regex": str(route.path_regex)}
#                 for route in api.routes]
#     return PrettyJSONResponse(url_list)


if __name__ == "__main__":
    uvicorn.run(app, host=config.get("host"),
                port=config.get("port"),
                proxy_headers=True,
                forwarded_allow_ips='*',
                log_config=get_log_config(),
                )
