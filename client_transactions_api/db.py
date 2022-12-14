from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from .config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    echo_pool=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=10
)

Session = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession
)


# FastAPI Dependency
async def get_database() -> AsyncSession:
    async with Session() as session:
        try:
            yield session
            await session.commit()
        except SQLAlchemyError as sql_ex:
            await session.rollback()
            raise sql_ex
        except HTTPException as http_ex:
            await session.rollback()
            raise http_ex
        finally:
            await session.close()
