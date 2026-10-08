from sqlalchemy import select, or_
from sqlalchemy.orm import Session
from app.models import User


def create(db: Session, name: str, email: str, phone: str, password_hash: str):
    user = User(name=name, email=email, phone=phone,
                password_hash=password_hash)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))


def get_by_email_or_phone(db: Session, email: str, phone: str) -> User | None:
    return db.scalar(
        select(User).where(or_(User.email == email, User.phone == phone))
    )
