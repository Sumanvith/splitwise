from pydantic import BaseModel, ConfigDict, EmailStr, Field
from datetime import datetime


class GroupCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class GroupRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    created_by: int
    created_at: datetime


class MemberAdd(BaseModel):
    email: EmailStr


class MemberRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    name: str
    email: EmailStr
    joined_at: datetime
