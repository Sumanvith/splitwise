from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from app.database import get_db
from app.models import User
from app.exceptions import UnauthorizedException, ForbiddenException
from app.core.security import decode_access_token
from app.models.group import GroupMember
from app.repositories import group_repo

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Annotated[Session, Depends(get_db)]) -> User:
    user_id = decode_access_token(token)
    user = db.get(User, user_id)
    if user is None:
        raise UnauthorizedException()
    return user


def get_group_member(group_id: int, db: DbSession, user: CurrentUser) -> GroupMember:
    member = group_repo.get_member(db, group_id, user.id)
    if member is None:
        raise ForbiddenException('You are not a member of this group')
    return member


DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]
GroupMemberDep = Annotated[GroupMember, Depends(get_group_member)]
