from pydantic import BaseModel, ConfigDict, Field, model_validator
from datetime import datetime
from enum import StrEnum


class SplitType(StrEnum):
    EQUAL = "equal"
    EXACT = "exact"


class ExactShare(BaseModel):
    user_id: int
    amount: float = Field(ge=0)


class ExpenseCreate(BaseModel):
    description: str = Field(min_length=1, max_length=200)
    total_amount: float = Field(gt=0)
    paid_by: int
    split_type: SplitType
    participants: list[int] | None = None
    shares: list[ExactShare] | None = None

    @model_validator(mode="after")
    def check_split_inputs(self):
        if self.split_type == SplitType.EQUAL:
            if not self.participants:
                raise ValueError("participants is required for equal split")
            if len(set(self.participants)) != len(self.participants):
                raise ValueError('participants must be unique')
        else:
            if not self.shares:
                raise ValueError("shares is required for exact split")
            ids = [share.user_id for share in self.shares]
            if len(set(ids)) != len(ids):
                raise ValueError('shares must have unique users')
        return self


class ExpenseShareRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    share_amount: int


class ExpenseRead(BaseModel):
    id: int
    group_id: int
    paid_by: int
    description: str
    total_amount: int
    split_type: str
    created_at: datetime
    shares: list[ExpenseShareRead]
