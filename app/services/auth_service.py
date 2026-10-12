from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from app.models import User
from app.repositories import user_repo
from app.schemas.user import UserCreate
from app.core.security import create_access_token, hash_password, verify_password
from app.exceptions import InvalidCredentialsException, UserAlreadyExistsException


async def register(db: AsyncSession, data: UserCreate) -> User:
    if await user_repo.get_by_email_or_phone(db, data.email, data.phone):
        raise UserAlreadyExistsException()

    password_hash = await run_in_threadpool(hash_password, data.password)

    try:
        user = await user_repo.create(
            db,
            name=data.name,
            email=data.email,
            phone=data.phone,
            password_hash=password_hash,
        )
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise UserAlreadyExistsException()
    return user


async def login(db: AsyncSession, email: str, password: str) -> str:
    user = await user_repo.get_by_email(db, email)
    if not user:
        raise InvalidCredentialsException()
    if not await run_in_threadpool(verify_password, password, user.password_hash):
        raise InvalidCredentialsException()
    return create_access_token(user.id)
