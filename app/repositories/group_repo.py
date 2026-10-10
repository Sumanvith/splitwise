from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.group import Group, GroupMember
from app.models.user import User


def create(db: Session, name: str, created_by: int) -> Group:
    group = Group(name=name, created_by=created_by)
    db.add(group)
    db.flush()
    return group


def get_by_id(db: Session, group_id: int) -> Group | None:
    return db.get(Group, group_id)


def list_for_user(db: Session, user_id: int) -> list[Group]:
    stmt = (
        select(Group)
        .join(GroupMember, GroupMember.group_id == Group.id)
        .where(GroupMember.user_id == user_id)
        .order_by(Group.created_at.desc())
    )
    return list(db.scalars(stmt).all())


def get_member(db: Session, group_id: int, user_id: int) -> GroupMember | None:
    return db.get(GroupMember, (group_id, user_id))


def add_member(db: Session, group_id: int, user_id: int) -> GroupMember:
    member = GroupMember(group_id=group_id, user_id=user_id)
    db.add(member)
    db.flush()
    return member


def list_members(db: Session, group_id: int):
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
    return db.execute(stmt).all()
