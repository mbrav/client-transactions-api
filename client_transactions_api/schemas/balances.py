from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class BalanceIn(BaseModel):
    user_id: int = Field(example=1, description="PK id user's id")
    value: float = Field(example=65.09, description="User's balance in currency")

    class Config:
        orm_mode = True


class BalanceOut(BalanceIn):
    created_at: datetime = Field(description="Date when balance was created")
    updated_at: Optional[datetime] = Field(description="Date when balance was updated")
    id: int = Field(example=1)
