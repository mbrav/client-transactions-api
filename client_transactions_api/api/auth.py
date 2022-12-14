from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from client_transactions_api import db, models, schemas
from client_transactions_api.services.auth import auth_service
from client_transactions_api.services.offline import OfflineTransactions

router = APIRouter()


@router.post(path='/token', response_model=schemas.Token)
async def get_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db_session: AsyncSession = Depends(db.get_database)
) -> schemas.Token:
    """Get token based on provided OAuth2 credentials"""

    user = await auth_service.authenticate_user(
        username=form_data.username,
        password=form_data.password,
        db_session=db_session)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'})
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='User is not active',
            headers={'WWW-Authenticate': 'Bearer'})
    access_token_expires = timedelta(minutes=auth_service.TOKEN_EXPIRE_MINUTES)
    data = {'sub': user.username}
    access_token = await auth_service.create_access_token(
        data=data,
        expires_delta=access_token_expires)

    # Store user auth data for offline transactions
    OfflineTransactions.add_auth_data(
        user_id=user.id,
        username=user.username,
        token=access_token)

    response = schemas.Token(
        access_token=access_token,
        token_type='bearer')
    return response


@router.post(
    path='/register',
    response_model=schemas.UserBase,
    status_code=status.HTTP_201_CREATED)
async def register_user(
    schema: schemas.UserLogin,
    db_session: AsyncSession = Depends(db.get_database)
) -> models.User:
    """Register new user"""

    user = await models.User.get(
        db_session, username=schema.username, raise_404=False)
    if user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Username '{schema.username}' already taken",
            headers={'WWW-Authenticate': 'Bearer'})

    hashed_password = auth_service.hash_password(schema.password)
    new_object = models.User(
        username=schema.username,
        password=hashed_password)

    return await new_object.save(db_session)


# from .deps import PermissionUser

# @router.post(
#     path='/password',
#     response_model=schemas.UserBase,
#     status_code=status.HTTP_200_OK)
# async def change_user_password(
#     schema: schemas.UserLogin,
#     user: models.User = Depends(PermissionUser),
#     db_session: AsyncSession = Depends(db.get_database)
# ) -> models.User:
#     """Change user password"""

#     if schema.username != user.username:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="You do not have permissions to change this user's password",
#             headers={'WWW-Authenticate': 'Bearer'})

#     hashed_password = auth_service.hash_password(schema.password)
#     update_object = models.User(
#         username=schema.username,
#         password=hashed_password)

#     return await update_object.update(db_session, **update_object.__dict__)
