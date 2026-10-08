from sqlalchemy.orm import Session
from app.models import User
from app.repositories import user_repo
from app.schemas.user import UserCreate
from app.core.security import create_access_token, hash_password, verify_password
from app.exceptions import InvalidCredentialsException, UserAlreadyExistsException


def register(db: Session, data: UserCreate) -> User:
    if user_repo.get_by_email_or_phone(db, data.email, data.phone):
        raise UserAlreadyExistsException()
    return user_repo.create(db, name=data.name, email=data.email, phone=data.phone, password_hash=hash_password(data.password))


def login(db: Session, email: str, password: str) -> str:
    user = user_repo.get_by_email(db, email)
    if not user or not verify_password(password, user.password_hash):
        raise InvalidCredentialsException()
    return create_access_token(user.id)
