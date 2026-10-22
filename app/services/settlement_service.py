from app.core.cache import balances_key, cache_delete, cache_get, cache_set

from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions import ValidationException
from app.models.settlement import Settlement
from app.repositories import group_repo, settlement_repo
from app.schemas.settlement import (
    BalanceRead,
    SettlementCreate,
    SuggestedSettlement,
    UserBalance,
)


def _to_paise(amount: float) -> int:
    return round(amount * 100)


def _suggest_settlements(nets: dict[int, int]) -> list[SuggestedSettlement]:
    creditors = sorted(
        [[uid, amt] for uid, amt in nets.items() if amt > 0],
        key=lambda x: x[1],
        reverse=True,
    )
    debtors = sorted(
        [[uid, -amt] for uid, amt in nets.items() if amt < 0],
        key=lambda x: x[1],
        reverse=True,
    )

    suggestions: list[SuggestedSettlement] = []
    while creditors and debtors:
        creditor, debtor = creditors[0], debtors[0]
        amount = min(creditor[1], debtor[1])
        suggestions.append(
            SuggestedSettlement(
                from_user=debtor[0], to_user=creditor[0], amount=amount
            )
        )
        creditor[1] -= amount
        debtor[1] -= amount
        if creditor[1] == 0:
            creditors.pop(0)
        if debtor[1] == 0:
            debtors.pop(0)
        creditors.sort(key=lambda x: x[1], reverse=True)
        debtors.sort(key=lambda x: x[1], reverse=True)
    return suggestions


async def get_balances(db: AsyncSession, group_id: int) -> BalanceRead:
    key = balances_key(group_id)
    cached = await cache_get(key)
    print(key, cached)
    if cached is not None:
        return BalanceRead.model_validate(cached)

    members = await group_repo.list_members(db, group_id)
    paid = await settlement_repo.get_paid_totals(db, group_id)
    owed = await settlement_repo.get_owed_totals(db, group_id)
    sent = await settlement_repo.get_sent_totals(db, group_id)
    received = await settlement_repo.get_received_totals(db, group_id)

    nets = {
        m.user_id: (
            paid.get(m.user_id, 0)
            - owed.get(m.user_id, 0)
            + sent.get(m.user_id, 0)
            - received.get(m.user_id, 0)
        )
        for m in members
    }
    result = BalanceRead(
        balances=[UserBalance(user_id=uid, net_amount=n)
                  for uid, n in nets.items()],
        suggested_settlements=_suggest_settlements(nets),
    )
    await cache_set(key, result.model_dump(mode="json"))
    return result


async def create_settlement(
    db: AsyncSession, group_id: int, data: SettlementCreate
) -> Settlement:
    members = await group_repo.list_members(db, group_id)
    member_ids = {m.user_id for m in members}
    if not ({data.from_user, data.to_user} <= member_ids):
        raise ValidationException("Both users must be group members")

    settlement = Settlement(
        group_id=group_id,
        from_user=data.from_user,
        to_user=data.to_user,
        amount=_to_paise(data.amount),
    )
    await settlement_repo.create(db, settlement)
    await db.commit()
    await cache_delete(balances_key(group_id))
    return settlement


async def list_settlements(db: AsyncSession, group_id: int) -> list[Settlement]:
    return await settlement_repo.list_by_group(db, group_id)
