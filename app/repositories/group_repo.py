from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.group import Group, GroupMember
from app.models.user import User


async def create(db: AsyncSession, name: str, created_by: int) -> Group:
    group = Group(name=name, created_by=created_by)
    db.add(group)
    await db.flush()
    return group


async def get_by_id(db: AsyncSession, group_id: int) -> Group | None:
    return await db.get(Group, group_id)


async def list_for_user(db: AsyncSession, user_id: int) -> list[Group]:
    stmt = (
        select(Group)
        .join(GroupMember, GroupMember.group_id == Group.id)
        .where(GroupMember.user_id == user_id)
        .order_by(Group.created_at.desc())
    )
    result = await db.scalars(stmt)
    return list(result.all())


async def get_member(db: AsyncSession, group_id: int, user_id: int) -> GroupMember | None:
    return await db.get(GroupMember, (group_id, user_id))


async def add_member(db: AsyncSession, group_id: int, user_id: int) -> GroupMember:
    member = GroupMember(group_id=group_id, user_id=user_id)
    db.add(member)
    await db.flush()
    return member


async def list_members(db: AsyncSession, group_id: int):
    stmt = (
        select(
            User.id.label('user_id'),
            User.name,
            User.email,
            GroupMember.joined_at,
        )
        .join(GroupMember, GroupMember.user_id == User.id)
        .where(GroupMember.group_id == group_id)
        .order_by(GroupMember.joined_at)
    )
    result = await db.execute(stmt)
    return result.all()
