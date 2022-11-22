from typing import Optional

from pydantic import BaseModel


class Token(BaseModel):
    """Token Payload"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Helper Class for FastAPI's deps"""
    username: str
