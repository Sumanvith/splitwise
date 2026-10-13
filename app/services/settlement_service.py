from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import group_repo, settlement_repo
from app.schemas.settlement import BalanceRead, SuggestedSettlement, UserBalance


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
    members = await group_repo.list_members(db, group_id)
    paid = await settlement_repo.get_paid_totals(db, group_id)
    owed = await settlement_repo.get_owed_totals(db, group_id)

    nets = {
        m.user_id: paid.get(m.user_id, 0) - owed.get(m.user_id, 0) for m in members
    }
    return BalanceRead(
        balances=[UserBalance(user_id=uid, net_amount=n)
                  for uid, n in nets.items()],
        suggested_settlements=_suggest_settlements(nets),
    )
