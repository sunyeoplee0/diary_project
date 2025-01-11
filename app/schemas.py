from pydantic import BaseModel, EmailStr
from datetime import datetime


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

    class Config:
        orm_mode = True
