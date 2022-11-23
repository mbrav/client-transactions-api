import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from client_transactions_api import db, models
from client_transactions_api.config import settings
from client_transactions_api.services.offline import OfflineException

context = CryptContext(schemes=['argon2'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f'{settings.API_PATH}/auth/token')

logger = logging.getLogger(__name__)


class AuthService:
    """"Auth Service Class"""

    def __init__(
            self,
            secret: str,
            algorithm: str = 'HS256',
            expire: int = 30):
        """Auth service initialization"""

        self.SECRET_KEY = secret
        self.CRYPT_ALGORITHM = algorithm
        self.TOKEN_EXPIRE_MINUTES = expire

        self.context = context
        self.oauth2_scheme = oauth2_scheme

    @staticmethod
    async def get_user(
        username: str,
        db_session: AsyncSession = Depends(db.get_database),
    ) -> models.User | OfflineException:
        """Get user from database"""

        return await models.User.get(db_session, username=username)

    @staticmethod
    def verify_password(
        plain_password: str,
        hashed_password: str
    ) -> bool:
        return context.verify(secret=plain_password, hash=hashed_password)

    @staticmethod
    def hash_password(password) -> str:
        """Hash password using with current password context"""
        return context.hash(password)

    async def authenticate_user(
        self,
        username: str,
        password: str,
        db_session: AsyncSession = Depends(db.get_database)
    ) -> models.User | None | OfflineException:
        """Authenticate user"""
        user = await self.get_user(username=username, db_session=db_session)
        if type(user) is OfflineException:
            logger.info('OfflineException return')
            return user
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user

    async def create_access_token(
        self,
        data: dict,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Encode Token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            delta = timedelta(minutes=self.TOKEN_EXPIRE_MINUTES)
            expire = datetime.utcnow() + delta
        to_encode.update({'exp': expire})
        encoded_jwt = jwt.encode(
            to_encode,
            self.SECRET_KEY,
            algorithm=self.CRYPT_ALGORITHM)
        return encoded_jwt


auth_service = AuthService(
    secret=settings.SECRET_KEY.get_secret_value(),
    algorithm=settings.CRYPT_ALGORITHM,
    expire=settings.TOKEN_EXPIRE_MINUTES)
