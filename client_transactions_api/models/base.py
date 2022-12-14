import logging
from datetime import datetime
from typing import List

from fastapi import HTTPException, status
from fastapi_pagination.bases import AbstractPage
from fastapi_pagination.ext.async_sqlalchemy import paginate
from sqlalchemy import Column, DateTime, Integer, func, inspect, select
from sqlalchemy.engine.result import Result
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.sql import text
from sqlalchemy.sql.selectable import Select

from client_transactions_api.services.offline import OfflineException

Base = declarative_base()
logger = logging.getLogger(__name__)


def to_snake_case(str: str) -> str:
    """Convert a class name string to snake case"""
    res = [str[0].lower()]
    for c in str[1:]:
        if c in ('ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
            res.append('_')
            res.append(c.lower())
        else:
            res.append(c)
    return ''.join(res)


class BaseModel(Base):
    """Abstract base model"""

    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow, nullable=True)

    @declared_attr
    def __tablename__(self) -> str:
        return to_snake_case(self.__name__) + 's'

    async def save(self, db_session: AsyncSession) -> "BaseModel | OfflineException":
        """Save object

        Args:
            db_session (AsyncSession): Current db session

        Raises:
            HTTPException: Raise SQLAlchemy error
        """
        try:
            db_session.add(self)
            await db_session.commit()
            await db_session.refresh(self)
            return self
        except IntegrityError as ex:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=repr(ex.orig))
        except SQLAlchemyError as ex:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=repr(ex))
        except ConnectionRefusedError:
            logger.warning('ConnectionRefusedError raised')
            return OfflineException()

    @classmethod
    async def get(
        cls,
        db_session: AsyncSession,
        db_query: Select | None = None,
        raise_404: bool = True,
        **kwarg
    ) -> "BaseModel | OfflineException":
        """Get object based on query or id identified by kwarg

        Args:
            db_session (AsyncSession): Current db session
            query (Select, optional): SQLAlchemy 2.0 select query. Defaults to None.
            raise_404 (bool, optional): Raise 404 if not found. Defaults to True.
            kwarg (optional): Object attribute and value by which
                to get object. Defaults to None.

        Raises:
            HTTPException: Raise SQLAlchemy error

        Returns:
            Database model or None
        """

        if not db_query:
            if not len(kwarg):
                db_query = select(cls)
            else:
                key, value = next(iter(kwarg.items()))
                db_query = select(cls).where(getattr(cls, key) == value)

        try:
            result = await db_session.execute(db_query)
            obj = result.scalars().first()
            if obj or not raise_404:
                # Returns Null or object
                return obj
            detail = ''
            if len(kwarg):
                key, value = next(iter(kwarg.items()))
                detail = f'{cls.__name__} with {key} = {value} not found'
            else:
                detail = f'{cls.__name__} not found'
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=detail)
        except SQLAlchemyError as ex:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=repr(ex))
        except ConnectionRefusedError:
            logger.warning('ConnectionRefusedError raised')
            return OfflineException()

    async def update(
        self,
        db_session: AsyncSession,
        **kwargs
    ) -> "BaseModel | OfflineException":
        """Update model object with provided attributes"""

        for k, v in kwargs.items():
            setattr(self, k, v)
        try:
            db_session.add(self)
            await db_session.commit()
            return self
        except SQLAlchemyError as ex:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=repr(ex))
        except ConnectionRefusedError:
            logger.warning('ConnectionRefusedError raised')
            return OfflineException()

    async def delete(self, db_session: AsyncSession) -> None | OfflineException:
        """Delete model object from database"""

        try:
            await db_session.delete(self)
            await db_session.commit()
        except SQLAlchemyError as ex:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=repr(ex))
        except ConnectionRefusedError:
            logger.warning('ConnectionRefusedError raised')
            return OfflineException()

    @classmethod
    async def _get_objects(
        cls,
        db_session: AsyncSession,
        db_query: Select | None = None,
        sort_by: str | None = None,
        desc: bool = True,
        paginated: bool = False,
        **kwargs
    ) -> "List[BaseModel | None] | None | AbstractPage | OfflineException":
        """Get list of objects of paginated

        Args:
            db_session (AsyncSession): Current db session
            db_query (Select, optional): SQLAlchemy 2.0 select query. Defaults to None.
            sort_by (str, optional): column by which to sort results.
            desc (bool, optional): Sort by descending. Defaults to True.

        Raises:
            HTTPException: Raise SQLAlchemy error

        Returns:
            paginate: fastapi_pagination result
            or
            Database models or None
        """

        filter_by = {k: v for k, v in kwargs.items() if v is not None}

        if not sort_by:
            sort_by = inspect(cls).primary_key[0].name
        if db_query is None:
            column = cls.__table__.columns.get(sort_by).name
            sort = 'desc'
            if not desc:
                sort = 'asc'
            if len(filter_by):
                db_query = select(cls).order_by(
                    text(f'{column} {sort}')).filter_by(**filter_by)
            else:
                db_query = select(cls).order_by(text(f'{column} {sort}'))

        try:
            if paginated:
                return await paginate(db_session, db_query)
            return await db_session.execute(db_query)
        except SQLAlchemyError as ex:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=repr(ex))
        except ConnectionRefusedError:
            logger.warning('ConnectionRefusedError raised')
            return OfflineException()

    @classmethod
    async def get_list(
        cls,
        db_session: AsyncSession,
        one: bool = False,
        **kwargs
    ) -> List["BaseModel"] | "BaseModel" | OfflineException:
        """Get list of objects

        Args:
            db_session (AsyncSession): Current db session
            one (bool, optional): Return as scalar with one object.
                Essentially checks if object exists or is None.
                Defaults to False.

        Returns:
            List[BaseModel]: As objects list of objects or object
        """

        result = await cls._get_objects(db_session, paginated=False, **kwargs)

        if type(result) is OfflineException:
            logger.info('OfflineException return')
            return result

        if one:
            return result.scalar()
        return result.scalars().all()

    @classmethod
    async def paginate(
        cls,
        db_session: AsyncSession,
        **kwargs
    ) -> "List[BaseModel | None] | None | AbstractPage | OfflineException":
        """Get paginated list of objects"""

        return await cls._get_objects(db_session, paginated=True, **kwargs)

    @classmethod
    async def get_distinct(
        cls,
        db_session: AsyncSession,
        *args
    ) -> Result | None | OfflineException:
        """Get list of specific model fields as rows"""
        try:
            return await db_session.execute(select(*args))
        except ConnectionRefusedError:
            logger.warning('ConnectionRefusedError raised')
            return OfflineException()

    @classmethod
    async def count(cls, db_session: AsyncSession) -> int | OfflineException:
        """Count number of objects"""
        db_query = select([func.count()]).select_from(cls)
        try:
            result = await db_session.execute(db_query)
            return result.scalar()
        except ConnectionRefusedError:
            logger.warning('ConnectionRefusedError raised')
            return OfflineException()
