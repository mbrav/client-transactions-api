import logging

from fastapi import HTTPException, status
from sqlalchemy import Column, Float, ForeignKey, Integer
from sqlalchemy.ext.asyncio import AsyncSession

from client_transactions_api.services.offline import OfflineException

from .base import BaseModel

logger = logging.getLogger(__name__)


class Balance(BaseModel):
    """Balance class"""

    user_id = Column(Integer, ForeignKey('users.id'), unique=True)

    value = Column(Float, default=0.0)

    def __init__(self,
                 user_id: int,
                 value: float = 0.0):
        self.user_id = user_id
        self.value = value

    @classmethod
    async def get_or_create(
        cls,
        db_session: AsyncSession,
        user_id: int
    ) -> "Balance | OfflineException":
        """Get or create new balance"""

        balance = await cls.get(db_session, raise_404=False, user_id=user_id)

        if type(balance) is OfflineException:
            logger.info('OfflineException return')
            return balance

        # Create new balance if none
        if not balance:
            balance = await cls(user_id=user_id).save(db_session)
        return balance

    @classmethod
    async def transaction(
        cls,
        db_session: AsyncSession,
        user_id: int,
        sum: float = 0
    ) -> "Balance | OfflineException":
        """Make a transaction for a user

        Args:
            db_session (AsyncSession): Current db session
            user_id (int): User id
            sum (float): Transaction sum (negative or positive)

        Returns:
            result (Balance): Balance object
        """

        balance = await cls.get_or_create(db_session, user_id=user_id)

        if type(balance) is OfflineException:
            logger.info('OfflineException return')
            return balance

        new_balance_value = balance.value + sum
        if new_balance_value < 0:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f'Not enough funds ({balance.value:.2f}) for a {sum:.2f} transaction!')

        balance.value = new_balance_value
        return await balance.update(db_session)
