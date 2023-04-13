import asyncio
from sqlalchemy.future import select

from api.database import get_async_session_context, get_user_db_context
from api.exceptions import AuthorityDenyException, InvalidParamsException
from api.models import ReferralCode, User
from api.response import response
from api.schema import UserRead, UserUpdate, UserCreate, LimitSchema
from api.users import auth_backend, fastapi_users, current_active_user, get_user_manager_context, current_super_user, generate_referral_code

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse, RedirectResponse

router = APIRouter()
auth_router = fastapi_users.get_auth_router(auth_backend)


@auth_router.get("/verify/{token}", tags=["auth"])
async def verify_user(token: str):
    async with get_async_session_context() as session:
        async with get_user_db_context(session) as db:
            async with get_user_manager_context(db) as user_manager:
                result = await user_manager.verifyEmail(token)
                if result:
                    return RedirectResponse("/login", status_code=303)
                else:
                    return HTMLResponse(f"<h2>Error: 验证失败</h2>", status_code=400)

router.include_router(
    auth_router, prefix="/auth", tags=["auth"]
)

router.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)

router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)


@router.get("/user", tags=["user"])
async def get_all_users(_user: User = Depends(current_super_user)):
    async with get_async_session_context() as session:
        r = await session.execute(select(User))
        results = r.scalars().all()
        return results


@router.patch("/user/{user_id}/reset-password", tags=["user"])
async def reset_password(user_id: int = None, new_password: str = None, _user: User = Depends(current_active_user)):
    if not new_password:
        raise InvalidParamsException("errors.newPasswordRequired")
    if _user.id != user_id and not _user.is_superuser:
        raise AuthorityDenyException("errors.noPermission")
    async with get_async_session_context() as session:
        async with get_user_db_context(session) as db:
            async with get_user_manager_context(db) as user_manager:
                result = await session.get(User, user_id)
                target_user = result
                if target_user is None:
                    raise InvalidParamsException("errors.userNotExist")
                target_user.hashed_password = user_manager.password_helper.hash(new_password)
                session.add(target_user)
                await session.commit()
                return response(200)


@router.post("/user/{user_id}/limit", tags=["user"])
async def update_limit(limit: LimitSchema, user_id: int = None, _user: User = Depends(current_super_user)):
    async with get_async_session_context() as session:
        target_user: User = await session.get(User, user_id)
        if target_user is None:
            raise InvalidParamsException("errors.userNotExist")

        for attr, value in limit.dict(exclude_unset=True).items():
            if value is not None:
                setattr(target_user, attr, value)

        # 使用**kargs类似的写法，但是跳过None值
        session.add(target_user)
        await session.commit()
        return response(200)


@router.post("/referral_code")
async def create_referral_code(user: User = Depends(current_active_user)):
    new_referral_code = asyncio.run(generate_referral_code())
    referral = ReferralCode(code=new_referral_code, user_id=user.id)

    async with get_async_session_context() as session:
        session.add(referral)
        session.commit()
        session.refresh(referral)

    return {"message": "Referral code created successfully", "referral_code": new_referral_code}


router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/user",
    tags=["user"],
)
