from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List

from database import SessionLocal
from models import Diary, User
from schemas import DiaryCreate, DiaryUpdate, DiaryResponse
from utils import verify_token, analyze_emotion_and_get_image

router = APIRouter(prefix="/diaries", tags=["Diary"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

http_bearer = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="유효하지 않은 토큰입니다.")

    user_id = payload.get("user_id")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="존재하지 않는 유저입니다.")

    return user


@router.post("/", response_model=DiaryResponse)
def create_diary(
    diary_data: DiaryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        analysis_result = analyze_emotion_and_get_image(diary_data.content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    emotion_val = analysis_result.get("emotion")
    image_url_val = analysis_result.get("image_url")

    new_diary = Diary(
        title=diary_data.title,
        content=diary_data.content,
        user_id=current_user.id,
        emotion = emotion_val,
        image_url = image_url_val
    )
    db.add(new_diary)
    db.commit()
    db.refresh(new_diary)
    return new_diary

@router.get("/", response_model=List[DiaryResponse])
def get_all_diaries(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    diaries = db.query(Diary).filter(Diary.user_id == current_user.id).all()
    return diaries


@router.get("/{diary_id}", response_model=DiaryResponse)
def get_diary(
    diary_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    diary = db.query(Diary).filter(Diary.id == diary_id, Diary.user_id == current_user.id).first()
    if not diary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="일기를 찾을 수 없습니다.")
    return diary


@router.put("/{diary_id}", response_model=DiaryResponse)
def update_diary(
    diary_id: int,
    diary_data: DiaryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    diary = db.query(Diary).filter(Diary.id == diary_id, Diary.user_id == current_user.id).first()
    if not diary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="일기를 찾을 수 없습니다.")

    diary.title = diary_data.title
    diary.content = diary_data.content
    db.commit()
    db.refresh(diary)
    return diary


@router.delete("/{diary_id}")
def delete_diary(
    diary_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    diary = db.query(Diary).filter(Diary.id == diary_id, Diary.user_id == current_user.id).first()
    if not diary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="일기를 찾을 수 없습니다.")

    db.delete(diary)
    db.commit()
    return {"message": "일기가 삭제되었습니다."}
