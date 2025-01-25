import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from jose import JWTError, jwt


load_dotenv()

X_API_KEY_VALUE = os.getenv("X-API-KEY")
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM")
EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", 30))

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def analyze_emotion_and_get_image(content: str):
    url = "https://daily-momento.duckdns.org/api/analyze_diary"

    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": X_API_KEY_VALUE
    }

    payload = {
        "content": content
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API 호출 실패: {response.status_code}, {response.text}")
