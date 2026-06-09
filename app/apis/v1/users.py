from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.security import get_password_hash
from app.models.users import User
from app.schemas.user import UserCreate, UserRead
from app.core.db.databases import async_get_db as get_db# DB 세션 가져오기

router = APIRouter()

@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    # 1. 이메일 중복 확인
    result = await db.execute(select(User).filter(User.email == user_in.email))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="이미 등록된 이메일입니다.")

    # 2. 비밀번호 해싱 및 사용자 데이터 생성
    # Pydantic 스키마를 딕셔너리로 변환
    user_data = user_in.model_dump()
    raw_password = user_data.pop("password")
    user_data["hashed_password"] = get_password_hash(raw_password)
    
    # 3. 모델 인스턴스 생성 및 DB 저장
    new_user = User(**user_data)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return new_user