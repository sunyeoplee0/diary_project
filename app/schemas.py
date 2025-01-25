from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    nickname: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    nickname: str

    class Config:
        orm_mode = True

class DiaryCreate(BaseModel):
    title: str
    content: str

class DiaryUpdate(BaseModel):
    title: str
    content: str

class DiaryResponse(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    user_id: int
    emotion: Optional[str]
    image_url: Optional[str]


    class Config:
        orm_mode = True
