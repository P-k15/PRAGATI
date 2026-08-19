from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: str  # "citizen" or "officer"

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(UserBase):
    id: str  # Firebase UID
    is_active: bool = True
    created_at: Optional[str] = None  # ISO format string

    class Config:
        from_attributes = True  # Updated from orm_mode for Pydantic v2

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None