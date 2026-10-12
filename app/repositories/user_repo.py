from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User


async def create(db: AsyncSession, name: str, email: str, phone: str, password_hash: str) -> User:
    user = User(name=name, email=email, phone=phone,
                password_hash=password_hash)
    db.add(user)
    await db.flush()
    return user


async def get_by_email(db: AsyncSession, email: str) -> User | None:
    return await db.scalar(select(User).where(User.email == email))


async def get_by_email_or_phone(db: AsyncSession, email: str, phone: str) -> User | None:
    return await db.scalar(
        select(User).where(or_(User.email == email, User.phone == phone))
    )
