from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.expense import Expense, ExpenseShare
from app.models.settlement import Settlement


async def get_paid_totals(db: AsyncSession, group_id: int) -> dict[int, int]:
    result = await db.execute(
        select(Expense.paid_by, func.sum(Expense.total_amount))
        .where(Expense.group_id == group_id)
        .group_by(Expense.paid_by)
    )
    return {user_id: int(total) for user_id, total in result.all()}


async def get_owed_totals(db: AsyncSession, group_id: int) -> dict[int, int]:
    result = await db.execute(
        select(ExpenseShare.user_id, func.sum(ExpenseShare.share_amount))
        .join(Expense, Expense.id == ExpenseShare.expense_id)
        .where(Expense.group_id == group_id)
        .group_by(ExpenseShare.user_id)
    )
    return {user_id: int(total) for user_id, total in result.all()}


async def get_sent_totals(db: AsyncSession, group_id: int) -> dict[int, int]:
    result = await db.execute(
        select(Settlement.from_user, func.sum(Settlement.amount))
        .where(Settlement.group_id == group_id)
        .group_by(Settlement.from_user)
    )
    return {user_id: int(total) for user_id, total in result.all()}


async def get_received_totals(db: AsyncSession, group_id: int) -> dict[int, int]:
    result = await db.execute(
        select(Settlement.to_user, func.sum(Settlement.amount))
        .where(Settlement.group_id == group_id)
        .group_by(Settlement.to_user)
    )
    return {user_id: int(total) for user_id, total in result.all()}


async def create(db: AsyncSession, settlement: Settlement) -> Settlement:
    db.add(settlement)
    await db.flush()
    return settlement


async def list_by_group(db: AsyncSession, group_id: int) -> list[Settlement]:
    result = await db.execute(
        select(Settlement)
        .where(Settlement.group_id == group_id)
        .order_by(Settlement.created_at.desc(), Settlement.id.desc())
    )
    return list(result.scalars().all())
