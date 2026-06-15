from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from sqlalchemy.future import select
from app.core.security import get_password_hash
from app.models.users import User
from app.schemas.user import UserCreate, UserRead
from app.core.db.databases import async_get_db as get_db# DB 세션 가져오기
from app.utils.validators import validate_nationality_names, validate_password, validate_employee_number
router = APIRouter()

@router.get("/users/check-email", summary="이메일 중복 확인")
async def check_email(email: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).filter(User.email == email))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="이미 등록된 이메일입니다.")
    return {"available": True}

@router.post("/users/signup", response_model=UserRead, status_code=status.HTTP_201_CREATED,summary="사용자 회원가입")
async def register_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    # 1. 국적 및 성명 검증 (함수 이름이 validate_nationality_names로 변경됨)
    validate_nationality_names(
        nationality=user_in.nationality,
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        middle_name=user_in.middle_name
    )
    
    # 2. 비밀번호 검증
    validate_password(user_in.password)
    # 3. 사번 검증
    validate_employee_number(user_in.employee_number)
    # 4. 이메일 중복 확인
    result = await db.execute(select(User).filter(User.email == user_in.email))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="이미 등록된 이메일입니다.")
    # 5. 사번 중복 체크 (이 부분을 추가하시면 됩니다!)
    existing_user_emp = await db.execute(select(User).filter(User.employee_number == user_in.employee_number))
    if existing_user_emp.scalars().first():
        raise HTTPException(status_code=400, detail="이미 등록된 사번입니다.")
    # 3. 전화번호 중복 체크 (추가된 부분)
    existing_user_phone = await db.execute(select(User).filter(User.phone_number == user_in.phone_number))
    if existing_user_phone.scalars().first():
        raise HTTPException(status_code=400, detail="이미 등록된 전화번호입니다.")

    # 6. 데이터 처리 및 이름 조합
    user_data = user_in.model_dump()
    raw_password = user_data.pop("password")
    
    # 이름 조합 (검증을 통과했으므로 안전하게 조합)
    user_data["name"] = f"{user_in.last_name or ''}{user_in.first_name}"
    
    # 비밀번호 해싱
    user_data["hashed_password"] = get_password_hash(raw_password)

    admin_count_result = await db.execute(
        select(func.count(User.id)).where(User.role == "admin")
    )
    admin_count = admin_count_result.scalar_one()
    user_data["role"] = "admin" if admin_count == 0 else "pending"
    
    # 7. DB 저장
    try:
        new_user = User(**user_data)
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
    except Exception as e:
        await db.rollback() # 에러 발생 시 롤백
        raise HTTPException(status_code=500, detail="회원가입 처리 중 데이터베이스 오류가 발생했습니다.")
    
    return new_user
