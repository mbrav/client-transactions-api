import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from client_transactions_api import db, models, schemas
from client_transactions_api.services.offline import OfflineTransactions

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

    # Check if there are any Offline transactions to run
    # Before running online transactions
    offline = OfflineTransactions.instance()
    await offline.gather(db_session, user.id)

    # Add User's balance to Offline Transactions pool
    balance = await models.Balance.get_or_create(db_session, user_id=user.id)
    offline.add_balance(user.id, balance.value)

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

    balance = await models.Balance.get_or_create(db_session, user_id=user.id)
    OfflineTransactions.instance().add_balance(user.id, balance.value)

    return balance
