import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from client_transactions_api import db, models, schemas
from client_transactions_api.services.offline import (
    InsufficientFundsException, OfflineException, OfflineTransactions,
    OfflineUserUnavailable)

from .deps import PermissionUser

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    path='',
    response_model=schemas.BalanceOut | schemas.OfflineBalanceOut,
    status_code=status.HTTP_201_CREATED)
async def balance_post(
    schema: schemas.BalanceIn,
    user: models.User = Depends(PermissionUser),
    db_session: AsyncSession = Depends(db.get_database)
) -> models.Balance:
    """Add new transaction to balance with POST request"""

    if type(user) is OfflineException:
        user_id = schema.user_id
        logger.info('OfflineException presented')

        # Carry out transaction
        offline_balance = OfflineTransactions.instance().transaction(user_id, schema.value)
        if type(offline_balance) == OfflineUserUnavailable:
            raise HTTPException(
                status_code=status.HTTP_206_PARTIAL_CONTENT,
                detail='Service down. User not available for offline processing')
        if type(offline_balance) == InsufficientFundsException:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=str(InsufficientFundsException))

        offline_balance = schemas.OfflineBalanceOut(
            **schema.dict(), balance=offline_balance).dict()
        raise HTTPException(
            status_code=status.HTTP_201_CREATED,
            detail=offline_balance)

    # Add User's balance to Offline Transactions pool
    balance = await models.Balance.get_or_create(db_session, user_id=user.id)
    OfflineTransactions.instance().add_balance(user.id, balance.value)

    return await models.Balance.transaction(db_session, user_id=user.id, sum=schema.value)


@router.get(
    path='/my',
    status_code=status.HTTP_200_OK,
    response_model=schemas.BalanceOut)
async def balance_get(
    user: models.User = Depends(PermissionUser),
    db_session: AsyncSession = Depends(db.get_database),
) -> models.Balance:
    """Retrieve user's Balance with GET request"""

    if type(user) is OfflineException:
        raise HTTPException(
            status_code=status.HTTP_206_PARTIAL_CONTENT,
            detail='Service down. User not available for offline processing')

    balance = await models.Balance.get_or_create(db_session, user_id=user.id)
    OfflineTransactions.instance().add_balance(user.id, balance.value)

    return balance
