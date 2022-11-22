from typing import Optional, Union

from sqlalchemy import Column, Float, ForeignKey, Integer, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, relationship

from .base import BaseModel
from .users import User


class Balance(BaseModel):
    """Balance class"""

    user_id = Column(Integer, ForeignKey('users.id'), unique=True)
    # user = relationship(User, back_populates='balance')

    value = Column(Float, default=0)

    def __init__(self,
                 user_id: int,
                 value: float = 0.0):
        self.user_id = user_id
        self.value = value

    # @classmethod
    # async def by_user(
    #     cls,
    #     db_session: AsyncSession,
    #     user_id: int,
    #     days_ago: Optional[Union[int, None]] = 0,
    #     limit: int = None,
    #     offset: int = 0
    # ):
    #     """Get balances of a user newer than days_ago

    #     Args:
    #         db_session (AsyncSession): Current db session
    #         user_id (int): User id
    #         days_ago (Union[int, None], optional): Ignore events before n days ago.
    #         Show all events if None. Defaults to 0.
    #         limit (int, optional): limit result. Defaults to None.
    #         offset (int, optional): offset result. Defaults to 0.

    #     Returns:
    #         query result
    #     """

    #     db_query = select(cls).join(
    #         cls.event).options(
    #         joinedload(cls.event)).filter(
    #         cls.user_id == user_id)

    #     if limit:
    #         db_query = db_query.limit(limit).offset(offset)

    #     return await cls.get_list(db_session, db_query=db_query)
