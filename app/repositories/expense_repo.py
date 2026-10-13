from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.expense import Expense, ExpenseShare


async def create(
    db: AsyncSession, expense: Expense, shares: list[ExpenseShare]
) -> Expense:
    db.add(expense)
    await db.flush()  # populates expense.id
    for share in shares:
        share.expense_id = expense.id
    db.add_all(shares)
    await db.flush()
    return expense


async def get(db: AsyncSession, group_id: int, expense_id: int) -> Expense | None:
    result = await db.execute(
        select(Expense).where(Expense.id == expense_id,
                              Expense.group_id == group_id)
    )
    return result.scalar_one_or_none()


async def list_by_group(db: AsyncSession, group_id: int) -> list[Expense]:
    result = await db.execute(
        select(Expense)
        .where(Expense.group_id == group_id)
        .order_by(Expense.created_at.desc(), Expense.id.desc())
    )
    return list(result.scalars().all())


async def get_shares(
    db: AsyncSession, expense_ids: list[int]
) -> dict[int, list[ExpenseShare]]:
    grouped: dict[int, list[ExpenseShare]] = {eid: [] for eid in expense_ids}
    if not expense_ids:
        return grouped
    result = await db.execute(
        select(ExpenseShare)
        .where(ExpenseShare.expense_id.in_(expense_ids))
        .order_by(ExpenseShare.expense_id, ExpenseShare.user_id)
    )
    for share in result.scalars().all():
        grouped[share.expense_id].append(share)
    return grouped
