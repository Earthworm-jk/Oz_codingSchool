from jose import jwt
import os
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.auth.jwt import get_current_user
from app.core.security import verify_password  # 여기서 security.py의 함수를 가져옵니다!
from app.models.users import User
from pydantic import BaseModel


# 민감 정보 확인용 스키마
class PasswordVerifyRequest(BaseModel):
    password: str

router = APIRouter(prefix="/profile", tags=["Profile"])

@router.post("/me/secure", summary="민감 정보 조회(비밀번호입력 필요)")
async def get_secure_info(data: PasswordVerifyRequest, current_user: User = Depends(get_current_user)):
    # 비밀번호 검증
    if not verify_password(data.password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="비밀번호가 일치하지 않습니다."
        )
    
    # 통과 시 민감 정보 반환 (필드명은 실제 모델에 맞게 수정하세요)
    return {
        "email": current_user.email,
        "name": current_user.name,
        "employee_number": current_user.employee_number 
    }