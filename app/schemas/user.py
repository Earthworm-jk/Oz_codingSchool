from pydantic import BaseModel, EmailStr, Field, model_validator
from typing import Optional
from app.utils.validators import (
    validate_employee_number,
    validate_password,
    validate_nationality_names,
    validate_age
)

# ==========================================
# 1. 회원가입 요청 스키마 (클라이언트 -> 서버)
# ==========================================
class UserCreate(BaseModel):
    employee_number: str = Field(..., description="8자리 숫자 사번", examples=["20260001"])
    email: EmailStr = Field(..., description="회사 이메일 계정", examples=["user@company.com"])
    password: str = Field(..., description="비밀번호 (8~20자, 대소문자/숫자/특수문자 포함)", examples=["SecurePass123!"])
    
    nationality: str = Field(..., description="국적 ('korean' 또는 'foreigner')", examples=["korean"])
    first_name: str = Field(..., description="이름 (내국인: 필수 / 외국인: 필수)", examples=["길동"])
    last_name: Optional[str] = Field(None, description="성 (내국인: 필수 / 외국인: 선택)", examples=["홍"])
    middle_name: Optional[str] = Field(None, description="미들네임 (내국인: 불가 / 외국인: 선택)", examples=[None])
    
    age: Optional[int] = Field(None, description="나이 (선택 사항)", examples=[30])
    phone_number: str = Field(..., description="전화번호", examples=["010-1234-5678"])
    gender: str = Field(..., description="성별 (Male, Female 등)", examples=["Male"])
    department: str = Field(..., description="소속 부서", examples=["Radiology"])

    # 💡 데이터 파싱 직후 비즈니스 룰 검증 연동
    @model_validator(mode="after")
    def check_user_business_rules(self):
        # 1단계에서 만든 검증 함수들을 차례대로 통과시킵니다.
        validate_employee_number(self.employee_number)
        validate_password(self.password)
        validate_age(self.age)
        
        validate_nationality_names(
            nationality=self.nationality,
            first_name=self.first_name,
            last_name=self.last_name,
            middle_name=self.middle_name
        )
        return self


# ==========================================
# 2. 회원정보 응답 스키마 (서버 -> 클라이언트)
# ==========================================
class UserResponse(BaseModel):
    id: str = Field(..., alias="uuid", description="유저 고유 ID (UUID7 문자열 규격)")
    employee_number: str
    email: EmailStr
    nationality: str
    first_name: str
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    age: Optional[int] = None
    phone_number: str
    gender: str
    department: str
    role: str = Field(..., description="유저 권한 (pending / staff / admin)")
    is_active: bool

    class Config:
        from_attributes = True