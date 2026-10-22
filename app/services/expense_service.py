from app.core.cache import balances_key, cache_delete

from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions import NotFoundException, ValidationException
from app.models.expense import Expense, ExpenseShare
from app.repositories import expense_repo, group_repo
from app.schemas.expense import (
    ExpenseCreate,
    ExpenseRead,
    ExpenseShareRead,
    SplitType,
)


def _to_paise(amount: float) -> int:
    return round(amount * 100)


def _split_equal(total: int, user_ids: list[int]) -> dict[int, int]:
    base, rem = divmod(total, len(user_ids))
    return {uid: base + (1 if i < rem else 0) for i, uid in enumerate(user_ids)}


def _to_read(expense: Expense, shares: list[ExpenseShare]) -> ExpenseRead:
    return ExpenseRead(
        id=expense.id,
        group_id=expense.group_id,
        paid_by=expense.paid_by,
        description=expense.description,
        total_amount=expense.total_amount,
        split_type=expense.split_type,
        created_at=expense.created_at,
        shares=[ExpenseShareRead.model_validate(s) for s in shares],
    )


async def create_expense(
    db: AsyncSession, group_id: int, data: ExpenseCreate
) -> ExpenseRead:
    total = _to_paise(data.total_amount)

    if data.split_type == SplitType.EQUAL:
        amounts = _split_equal(total, data.participants)
    else:
        amounts = {s.user_id: _to_paise(s.amount) for s in data.shares}
        if sum(amounts.values()) != total:
            raise ValidationException("Shares must sum to total_amount")

    members = await group_repo.list_members(db, group_id)
    member_ids = {m.user_id for m in members}
    if not ({data.paid_by, *amounts} <= member_ids):
        raise ValidationException(
            "Payer and participants must be group members")

    expense = Expense(
        group_id=group_id,
        paid_by=data.paid_by,
        description=data.description,
        total_amount=total,
        split_type=data.split_type.value,
    )
    shares = [
        ExpenseShare(user_id=uid, share_amount=amt) for uid, amt in amounts.items()
    ]
    await expense_repo.create(db, expense, shares)
    await db.commit()
    await cache_delete(balances_key(group_id))
    return _to_read(expense, shares)


async def get_expense(db: AsyncSession, group_id: int, expense_id: int) -> ExpenseRead:
    expense = await expense_repo.get(db, group_id, expense_id)
    if expense is None:
        raise NotFoundException("Expense not found")
    shares = (await expense_repo.get_shares(db, [expense.id]))[expense.id]
    return _to_read(expense, shares)


async def list_expenses(db: AsyncSession, group_id: int) -> list[ExpenseRead]:
    expenses = await expense_repo.list_by_group(db, group_id)
    shares = await expense_repo.get_shares(db, [e.id for e in expenses])
    return [_to_read(e, shares[e.id]) for e in expenses]
