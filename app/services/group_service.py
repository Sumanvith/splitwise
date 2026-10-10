from sqlalchemy.orm import Session
from app.exceptions import ConflictException, NotFoundException
from app.models.group import Group, GroupMember
from app.repositories import group_repo, user_repo


def create_group(db: Session, name: str, user_id: int) -> Group:
    group = group_repo.create(db, name, user_id)
    group_repo.add_member(db, group.id, user_id)
    db.commit()
    db.refresh(group)
    return group


def list_my_groups(db: Session, user_id: int) -> list[Group]:
    return group_repo.list_for_user(db, user_id)


def add_member(db: Session, group_id: int, email: str) -> GroupMember:
    user = user_repo.get_by_email(db, email)
    if user is None:
        raise NotFoundException('User not found')
    if group_repo.get_member(db, group_id, user.id):
        raise ConflictException('User is already in this group')
    member = group_repo.add_member(db, group_id, user.id)
    db.commit()
    return member


def list_members(db: Session, group_id: int):
    return group_repo.list_members(db, group_id)
