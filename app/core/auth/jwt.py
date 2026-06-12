from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.db.databases import async_get_db
from app.models.users import User 
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"

oauth2_scheme = HTTPBearer()

async def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    db: AsyncSession = Depends(async_get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="토큰 검증 실패",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # 1. 토큰 추출 및 'bearer ' 접두사 제거 (보안 정규화)
    raw_token = token.credentials
    if raw_token.lower().startswith("bearer "):
        raw_token = raw_token.split(" ")[1]
    
    #print(f"DEBUG: 토큰 수신 시도! 토큰 정보: {raw_token[:10]}...")

    try:
        payload = jwt.decode(raw_token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        #print(f"DEBUG: 토큰에서 읽은 이메일 -> {email}") 
    except JWTError as e:
        #print(f"DEBUG: JWT 해독 실패 사유 -> {str(e)}") # <--- 이 로그를 꼭 보세요!
        raise credentials_exception

    # 3. DB 조회
    result = await db.execute(select(User).filter(User.email == email))
    user = result.scalars().first()
    
    if user is None:
        #print(f"DEBUG: DB 조회 실패! {email}에 해당하는 사용자가 없음.") 
        raise credentials_exception
    
    #print(f"DEBUG: 유저 찾기 성공 -> {user.email}")
    return user
