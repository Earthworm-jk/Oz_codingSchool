from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.auth.jwt import get_current_user
from app.models.users import User
from app.schemas.user import UserPasswordUpdate, UserRead, UserUpdate
from app.core.db.databases import async_get_db
from app.core.security import get_password_hash, verify_password
from app.utils.validators import validate_password

router = APIRouter(tags=["me"])

@router.get("/me", response_model=UserRead,summary="백엔드 정보조회")
async def get_my_info(current_user: User = Depends(get_current_user)):
    """
    현재 로그인한 사용자의 정보를 조회합니다.
    """
    return current_user

@router.patch("/me", response_model=UserRead, summary="내 정보 수정(전화번호, 부서)")
async def update_my_info(
    user_in: UserUpdate, 
    current_user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(async_get_db)
):
    # 1. 수정할 데이터 추출 (입력된 값만 반영)
    update_data = user_in.model_dump(exclude_unset=True)
    
    # 2. current_user 객체의 필드 업데이트
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    # 3. DB 저장 및 커밋
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user) # 여기서 DB의 최신 상태를 current_user에 다시 불러옵니다.
    
    # 4. 업데이트된 객체 반환
    return current_user

@router.patch("/me/password", summary="내 비밀번호 변경")
async def update_my_password(
    password_in: UserPasswordUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(async_get_db),
):
    if not verify_password(password_in.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="현재 비밀번호가 일치하지 않습니다.",
        )

    validate_password(password_in.new_password)
    current_user.hashed_password = get_password_hash(password_in.new_password)
    db.add(current_user)
    await db.commit()

    return {"message": "비밀번호가 변경되었습니다."}

@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT, summary="내 정보 삭제(탈퇴)")
async def delete_my_info(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(async_get_db)):
    # 1. DB에서 현재 사용자 객체를 삭제합니다.
    await db.delete(current_user)
    
    # 2. 변경사항을 DB에 반영(커밋)합니다.
    await db.commit()
    
    # 3. 204 No Content를 반환합니다.
    return None
