from app.core.cache import balances_key, cache_delete

from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions import ConflictException, NotFoundException
from app.models.group import Group, GroupMember
from app.repositories import group_repo, user_repo


async def create_group(db: AsyncSession, name: str, user_id: int) -> Group:
    group = await group_repo.create(db, name, user_id)
    await group_repo.add_member(db, group.id, user_id)
    await db.commit()
    await db.refresh(group)
    return group


async def list_my_groups(db: AsyncSession, user_id: int) -> list[Group]:
    return await group_repo.list_for_user(db, user_id)


async def add_member(db: AsyncSession, group_id: int, email: str) -> GroupMember:
    user = await user_repo.get_by_email(db, email)
    if user is None:
        raise NotFoundException('User not found')

    existing_member = await group_repo.get_member(db, group_id, user.id)
    if existing_member:
        raise ConflictException('User is already in this group')

    member = await group_repo.add_member(db, group_id, user.id)
    await db.commit()
    await cache_delete(balances_key(group_id))
    return member


async def list_members(db: AsyncSession, group_id: int):
    return await group_repo.list_members(db, group_id)
