import random
import string

from . import db, models, schemas
from .services.auth import auth_service


async def create_superuser(
    username: str,
    password: str,
) -> None:
    """
    Create a super user in database
    """

    async with db.Session() as db_session:
        user = await models.User.get(db_session, raise_404=False)

        if not user:
            hashed_password = auth_service.hash_password(password)
            user_in = schemas.UserCreate(
                username=username,
                password=hashed_password,
                is_admin=True)
            new_user = models.User(**user_in.dict())
            await new_user.save(db_session)


def random_lower_string(num: int = 20) -> str:
    return ''.join(random.choices(string.ascii_lowercase, k=num))


def random_numbers(num: int = 20) -> str:
    return ''.join(random.choices(string.digits, k=num))


def random_id_string(num: int = 20) -> str:
    return ''.join(random.choices(string.ascii_letters, k=num))


def random_email() -> str:
    return f'{random_lower_string(10)}@{random_lower_string(5)}.com'


def random_phone(num: int = 20) -> str:
    return '+' + random_numbers(11)
