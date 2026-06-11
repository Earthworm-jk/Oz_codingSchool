from datetime import datetime, timedelta
from jose import jwt

SECRET_KEY = "SECRET_KEY_HERE"  # 실제 배포 시에는 환경변수(.env)로 관리하세요
ALGORITHM = "HS256"

def create_access_token(data: dict):
    to_encode = data.copy()
    # 토큰 유효기간 30분 설정
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)