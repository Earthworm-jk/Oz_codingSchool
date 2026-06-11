from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.users import User
from app.core.db.databases import async_get_db
from app.core.security import verify_password
from app.core.auth.jwt import create_access_token, create_refresh_token

# 경로를 /users로 설정 (프론트/설계서 요구사항)
router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(async_get_db)):
    # form_data.username에는 프론트에서 보낸 'username'(이메일)이 들어옵니다.
    # form_data.password에는 'password'가 들어옵니다.
    
    # 1. 이메일(username)로 유저 찾기
    result = await db.execute(select(User).filter(User.email == form_data.username))
    user = result.scalars().first()
    
    # 2. 유저 검증
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="이메일 혹은 비밀번호가 틀렸습니다."
        )
    
    # 3. 토큰 발급
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    
    return {
        "access_token": access_token, 
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
@router.post("/logout", tags=["User Login"])
async def logout():
    # 여기서 서버는 상태값을 따로 변경하지 않아도 됩니다.
    # 클라이언트에게 로그아웃했음을 알리는 성공 응답만 전달합니다.
    return {"message": "로그아웃 성공."}