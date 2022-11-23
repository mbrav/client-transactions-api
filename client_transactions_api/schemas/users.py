from typing import Optional

from pydantic import BaseModel, Field


class UserBase(BaseModel):
    username: str = Field(
        example='user',
        description='A valid username')

    class Config:
        orm_mode = True


class UserLogin(UserBase):
    password: str = Field(
        example='password',
        description='A valid password')


class UserUpdate(UserLogin):
    password: str = Field(
        default=None,
        example='myNewPa$$word',
        description='A new valid password')


class UserCreate(UserUpdate):
    is_admin: bool = Field(
        default=False,
        description='Specify if a user is an admin')
    is_active: bool = Field(
        default=True,
        description='Specify if a user is active')


class User(UserCreate):
    """Complete user model"""
    id: str = Field(
        example=2,
        description='Id of the user')
