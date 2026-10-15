from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class SettlementCreate(BaseModel):
    from_user: int
    to_user: int
    amount: float = Field(gt=0)  # rupees

    @model_validator(mode="after")
    def check_users(self):
        if self.from_user == self.to_user:
            raise ValueError("from_user and to_user must be different")
        return self


class SettlementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    group_id: int
    from_user: int
    to_user: int
    amount: int  # paise
    created_at: datetime


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
