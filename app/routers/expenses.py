from fastapi import APIRouter

from app.core.dependencies import DbSession, GroupMemberDep
from app.schemas.expense import ExpenseCreate, ExpenseRead
from app.services import expense_service

router = APIRouter(prefix="/groups/{group_id}/expenses", tags=["expenses"])


@router.post("", response_model=ExpenseRead, status_code=201)
async def create_expense(
    group_id: int, data: ExpenseCreate, db: DbSession, _: GroupMemberDep
):
    return await expense_service.create_expense(db, group_id, data)


@router.get("", response_model=list[ExpenseRead])
async def list_expenses(group_id: int, db: DbSession, _: GroupMemberDep):
    return await expense_service.list_expenses(db, group_id)


@router.get("/{expense_id}", response_model=ExpenseRead)
async def get_expense(
    group_id: int, expense_id: int, db: DbSession, _: GroupMemberDep
):
    return await expense_service.get_expense(db, group_id, expense_id)
