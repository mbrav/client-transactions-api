from typing import Optional

from fastapi import APIRouter, Depends, status
from fastapi_pagination import LimitOffsetPage, add_pagination
from sqlalchemy.ext.asyncio import AsyncSession

from client_transactions_api import db, models, schemas

from .deps import (FilterQuery, PermissionAdmin, PermissionUser,
                   SortByDescQuery, SortByQuery)

router = APIRouter()


@router.post(
    path='',
    response_model=schemas.BalanceOut,
    status_code=status.HTTP_201_CREATED)
async def balance_post(
    schema: schemas.BalanceIn,
    user: Optional[models.User] = Depends(PermissionUser),
    db_session: AsyncSession = Depends(db.get_database)
) -> models.Balance:
    """Create new Balance with POST request"""

    new_object = models.Balance(**schema.dict())
    return await new_object.save(db_session)


@router.get(
    path='/{id}',
    status_code=status.HTTP_200_OK,
    response_model=schemas.BalanceOut)
async def balance_get(
    id: int,
    user: models.User = Depends(PermissionUser),
    db_session: AsyncSession = Depends(db.get_database),
) -> models.Balance:
    """Retrieve Balance with GET request"""

    get_object = await models.Balance.get(db_session, id=id)
    return get_object


@router.delete(
    path='/{id}',
    status_code=status.HTTP_204_NO_CONTENT)
async def balance_delete(
    id: int,
    user: models.User = Depends(PermissionAdmin),
    db_session: AsyncSession = Depends(db.get_database),
) -> models.Balance:
    """Retrieve Balance with GET request"""

    get_object = await models.Balance.get(db_session, id=id)
    return await get_object.delete(db_session)


@router.patch(
    path='/{id}',
    status_code=status.HTTP_202_ACCEPTED,
    response_model=schemas.BalanceOut)
async def balance_patch(
    id: int,
    schema: schemas.BalanceIn,
    user: models.User = Depends(PermissionUser),
    db_session: AsyncSession = Depends(db.get_database),
) -> models.Balance:
    """Modify Balance with PATCH request"""

    get_object = await models.Balance.get(db_session, id=id)
    return await get_object.update(db_session, **schema.dict())


@router.get(
    path='',
    status_code=status.HTTP_200_OK,
    response_model=LimitOffsetPage[schemas.BalanceOut])
async def Balances_list(
    user: models.User = Depends(PermissionAdmin),
    db_session: AsyncSession = Depends(db.get_database),
    sort_by: Optional[str] = SortByQuery,
    desc: Optional[bool] = SortByDescQuery,
    user_id: Optional[int] = FilterQuery
):
    """List Balances with GET request"""

    return await models.Balance.paginate(
        db_session,
        desc=desc,
        sort_by=sort_by,
        user_id=user_id,
    )


@router.get(
    path='/my',
    status_code=status.HTTP_200_OK,
    response_model=LimitOffsetPage[schemas.BalanceOut])
async def Balances_list_by_user(
    user: models.User = Depends(PermissionUser),
    db_session: AsyncSession = Depends(db.get_database),
    sort_by: Optional[str] = SortByQuery,
    desc: Optional[bool] = SortByDescQuery,
):
    """List Balances by user with GET request"""

    return await models.Balance.paginate(
        db_session,
        desc=desc,
        sort_by=sort_by,
        user_id=user.id,
    )
    
add_pagination(router)
