import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from client_transactions_api import db, models, schemas
from client_transactions_api.services.offline import (OfflineException,
                                                      OfflineTransaction,
                                                      OfflineTransactions)

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
        logger.info('OfflineException presented')

        detail = schemas.OfflineBalanceOut(**schema.dict()).dict()
        raise HTTPException(
            status_code=status.HTTP_201_CREATED,
            detail=detail)

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

    return await models.Balance.get_or_create(db_session, user_id=user.id)
