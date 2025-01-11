from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from database import SessionLocal
from models import User
from schemas import UserCreate, UserLogin, UserResponse
from utils import create_access_token, verify_token

router = APIRouter(prefix="/user", tags=["User"])

http_bearer = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/signup", response_model=UserResponse)
def signup(user_data: UserCreate, db: Session = Depends(get_db)):

    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 가입된 이메일입니다."
        )


    hashed_password = pwd_context.hash(user_data.password)


    new_user = User(
        email=user_data.email,
        password=hashed_password,
        nickname=user_data.nickname
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login")
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다."
        )

    if not pwd_context.verify(user_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다."
        )


    access_token = create_access_token({"user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
def logout(credentials: HTTPAuthorizationCredentials = Depends(http_bearer)):

    token = credentials.credentials

    if not verify_token(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다."
        )


    return {"message": "로그아웃 되었습니다"}