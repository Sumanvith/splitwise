from fastapi import APIRouter, status
from app.core.dependencies import CurrentUser, DbSession, GroupMemberDep
from app.schemas.group import GroupCreate, GroupRead, MemberRead, MemberAdd
from app.services import group_service

router = APIRouter(prefix="/groups", tags=["groups"])


@router.post('', response_model=GroupRead, status_code=status.HTTP_201_CREATED)
async def create_group(data: GroupCreate, db: DbSession, user: CurrentUser):
    return await group_service.create_group(db, data.name, user.id)


@router.get('', response_model=list[GroupRead])
async def list_my_groups(db: DbSession, user: CurrentUser):
    return await group_service.list_my_groups(db, user.id)


@router.get('/{group_id}/members', response_model=list[MemberRead])
async def list_members(group_id: int, db: DbSession, _: GroupMemberDep):
    return await group_service.list_members(db, group_id)


@router.post('/{group_id}/members', response_model=MemberRead, status_code=status.HTTP_201_CREATED)
async def add_member(group_id: int, data: MemberAdd, db: DbSession, _: GroupMemberDep):
    await group_service.add_member(db, group_id, data.email)
    members = await group_service.list_members(db, group_id)
    return next(m for m in members if m.email == data.email)
