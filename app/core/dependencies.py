from typing import Annotated
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import User
from app.exceptions import UnauthorizedException, ForbiddenException
from app.core.security import decode_access_token
from app.models.group import GroupMember
from app.repositories import group_repo

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

DbSession = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], db: DbSession
) -> User:
    user_id = decode_access_token(token)
    user = await db.get(User, user_id)
    if user is None:
        raise UnauthorizedException()
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


async def get_group_member(
    group_id: int, db: DbSession, user: CurrentUser
) -> GroupMember:
    member = await group_repo.get_member(db, group_id, user.id)
    if member is None:
        raise ForbiddenException('You are not a member of this group')
    return member


GroupMemberDep = Annotated[GroupMember, Depends(get_group_member)]
