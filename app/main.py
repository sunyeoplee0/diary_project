from fastapi import FastAPI
from database import  engine
from models import Base
from routers import user_router, diary_router

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(user_router.router)
app.include_router(diary_router.router)

