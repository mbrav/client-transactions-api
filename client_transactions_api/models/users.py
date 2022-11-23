from sqlalchemy import BigInteger, Boolean, Column, String
from sqlalchemy.orm import relationship

from .base import BaseModel


class User(BaseModel):
    """User class"""

    username = Column(String(20), nullable=False)
    hashed_password = Column(String(130), nullable=True)

    is_active = Column(Boolean(), default=True)
    is_admin = Column(Boolean(), default=False)

    def __init__(self,
                 username: str,
                 password: str | None = None,
                 is_active: bool = True,
                 is_admin: bool = False):
        self.username = username
        self.hashed_password = password
        self.is_active = is_active
        self.is_admin = is_admin
