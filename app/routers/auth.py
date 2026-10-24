from typing import Annotated
from fastapi import APIRouter, status, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from app.services import auth_service
from app.schemas.user import UserCreate, UserResponse, Token
from app.core.dependencies import CurrentUser, DbSession
from app.core.limiter import limiter
import logging

logger = logging.getLogger("app")

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def register(request: Request, data: UserCreate, db: DbSession):
    user = await auth_service.register(db, data)
    logger.info("user registered", extra={
                "event": "register", "user": data.email})
    return user


@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
async def login(
    request: Request,
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DbSession,
):
    access_token = await auth_service.login(db, form.username, form.password)
    logger.info("login ok", extra={"event": "login", "user": form.username})
    return Token(access_token=access_token)


@router.get("/me", response_model=UserResponse)
async def me(current_user: CurrentUser):
    return current_user
