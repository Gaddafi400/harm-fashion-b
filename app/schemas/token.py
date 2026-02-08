"""Token schemas"""
from pydantic import BaseModel

class Token(BaseModel):
    """Token response schema"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Token payload data"""
    username: str | None = None
    user_id: int | None = None
