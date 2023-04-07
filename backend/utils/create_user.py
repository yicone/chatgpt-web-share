from api.schema import UserCreate
from api.users import get_user_manager_context
from api.database import get_user_db_context, get_async_session_context
from utils.logger import get_logger
import api.globals as g

config = g.config

logger = get_logger(__name__)


async def create_user(username, nickname: str, email: str, password: str, is_superuser: bool = False, **kwargs):
    try:
        async with get_async_session_context() as session:
            async with get_user_db_context(session) as user_db:
                async with get_user_manager_context(user_db) as user_manager:
                    user = await user_manager.create(
                        UserCreate(
                            username=username, nickname=nickname,
                            email=email, password=password, 
                            is_superuser=is_superuser,
                            max_conv_count=config.get('new_user_max_conv_count', 1), 
                            available_ask_count=config.get('new_user_available_ask_count', 3),
                            available_gpt4_ask_count=config.get('new_user_available_gpt4_ask_count', 0),
                            **kwargs
                        )
                    )
                    logger.info(f"User created: {user}")
                    return user
    except Exception as e:
        logger.info(f"Create User {username} Error: {e}")
        return None
