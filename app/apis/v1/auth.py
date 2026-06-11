from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.users import User
from app.core.db.databases import async_get_db
from app.core.security import verify_password, create_access_token, create_refresh_token
from pydantic import BaseModel

router = APIRouter(tags=["User Login"])

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login")
async def login(login_in: LoginRequest, db: AsyncSession = Depends(async_get_db)):
    # 1. 이메일로 유저 찾기
    result = await db.execute(select(User).filter(User.email == login_in.email))
    user = result.scalars().first()
    
    # 2. 유저가 없거나 비밀번호가 틀린 경우
    if not user or not verify_password(login_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="이메일 혹은 비밀번호가 틀렸습니다."
        )
    
    # 3. 토큰 발급 (access와 refresh 둘 다 발급)
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    
    return {
        "access_token": access_token, 
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }