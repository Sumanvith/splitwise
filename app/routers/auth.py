from typing import Annotated
from fastapi import APIRouter, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.services import auth_service
from app.schemas.user import UserCreate, UserResponse, Token
from app.core.dependencies import CurrentUser, DbSession

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(data: UserCreate, db: DbSession):
    return await auth_service.register(db, data)


@router.post("/login", response_model=Token)
async def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], db: DbSession):
    access_token = await auth_service.login(db, form.username, form.password)
    return Token(access_token=access_token)


@router.get("/me", response_model=UserResponse)
async def me(current_user: CurrentUser):
    return current_user
