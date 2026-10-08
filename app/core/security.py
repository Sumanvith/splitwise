from datetime import datetime, timedelta
import jwt
from pwdlib import PasswordHash
from app.config import settings
from app.exceptions import UnauthorizedException

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def create_access_token(user_id: int) -> str:
    expire = int(datetime.now().timestamp()) + \
        settings.access_token_expire_minutes * 60
    payload = {"sub": str(user_id), "exp": expire}
    token = jwt.encode(payload, settings.secret_key,
                       algorithm=settings.algorithm)
    return token


def decode_access_token(token: str) -> int:
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        return int(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise UnauthorizedException()
