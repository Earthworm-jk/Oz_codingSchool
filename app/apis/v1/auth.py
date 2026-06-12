from fastapi import APIRouter, Depends, HTTPException, status, Body, Form # Form 추가
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.users import User
from app.core.db.databases import async_get_db
from app.core.security import verify_password, create_access_token, create_refresh_token
from pydantic import BaseModel
# 경로를 /users로 설정 (프론트/설계서 요구사항)
router = APIRouter()

@router.post("/login", summary="사용자 로그인")
async def login(
    useremail: str = Form(..., alias="username",openapi_extra={"title": "email"}), # Form으로 이메일만 지정
    password: str = Form(...), # Form으로 비밀번호만 지정
    db: AsyncSession = Depends(async_get_db)
):
    # 이제 form_data.username 대신 그냥 username 변수를 사용합니다.
    result = await db.execute(select(User).filter(User.email == useremail))
    user = result.scalars().first()
    
    if not user or not verify_password(password, user.hashed_password):
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
        "token_type": "bearer",
        "message": "로그인 성공!"
    }
@router.post("/logout", summary="사용자 로그아웃")
async def logout():
    # 여기서 서버는 상태값을 따로 변경하지 않아도 됩니다.
    # 클라이언트에게 로그아웃했음을 알리는 성공 응답만 전달합니다.
    return {"message": "로그아웃 성공."}