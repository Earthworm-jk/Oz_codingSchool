from fastapi import APIRouter, Depends, HTTPException, status
# 💡 비동기 세션 스펙으로 변경
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

# 프로젝트 모듈 가져오기
from app.models.users import User,UserRole, NationalityType
from app.schemas.user import UserCreate, UserResponse
from app.core.security import get_password_hash
# 💡 async_get_db로 변경
from app.core.db.databases import async_get_db 

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

# 💡 async def 로 비동기 함수 전환
@router.post("/signup", response_model=UserResponse,summary="회원가입 API", status_code=status.HTTP_201_CREATED)
async def signup(user_in: UserCreate, db: AsyncSession = Depends(async_get_db)):
    """
    비동기(Async) 환경에 맞춘 실전 프로덕션 레벨 회원가입 API
    """
    
    # 1. 사번 중복 체크 (비동기 방식 쿼리 조회)
    emp_stmt = select(User).where(User.employee_number == user_in.employee_number)
    emp_result = await db.execute(emp_stmt)
    existing_emp = emp_result.scalars().first()
    
    if existing_emp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 등록된 사번입니다."
        )
        
    # 2. 이메일 중복 체크 (비동기 방식 쿼리 조회)
    email_stmt = select(User).where(User.email == user_in.email)
    email_result = await db.execute(email_stmt)
    existing_email = email_result.scalars().first()
    
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 존재하는 이메일 계정입니다."
        )

    # 3. 비밀번호 안전하게 해싱
    hashed_pw = get_password_hash(user_in.password)

    # 4. DB ORM 모델 객체 생성
    new_user = User(
        employee_number=user_in.employee_number,
        email=user_in.email,
        hashed_password=hashed_pw,
        nationality=user_in.nationality,
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        middle_name=user_in.middle_name,
        age=user_in.age,
        phone_number=user_in.phone_number,
        gender=user_in.gender,
        department=user_in.department,
        role=UserRole.PENDING
    )

    # 5. 데이터베이스에 비동기 저장 (await 필수)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user) 

    return new_user