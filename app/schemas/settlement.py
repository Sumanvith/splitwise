from pydantic import BaseModel


class UserBalance(BaseModel):
    user_id: int
    net_amount: int  # paise; positive = is owed, negative = owes


class SuggestedSettlement(BaseModel):
    from_user: int
    to_user: int
    amount: int  # paise


class BalanceRead(BaseModel):
    balances: list[UserBalance]
    suggested_settlements: list[SuggestedSettlement]
