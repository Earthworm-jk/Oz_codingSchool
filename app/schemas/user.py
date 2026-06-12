from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from enum import Enum

# Enum 정의 (모델과 동일한 값)
class NationalityEnum(str, Enum):
    korean = "korean"
    foreigner = "foreigner"

class GenderEnum(str, Enum):
    male = "male"
    female = "female"

class DepartmentEnum(str, Enum):
    developer = "developer"
    medical_team = "medical team" # 띄어쓰기 주의
    researcher = "researcher"

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str = Field(..., max_length=20)
    last_name: Optional[str] = Field(None, max_length=20)
    middle_name: Optional[str] = Field(None, max_length=20)
    # 정규식 패턴 추가 유지
    employee_number: str = Field(..., pattern=r"^\d{8}$") 
    phone_number: str
    nationality: NationalityEnum  # str 대신 Enum 사용
    gender: GenderEnum            # str 대신 Enum 사용
    department: DepartmentEnum    # str 대신 Enum 사용

class UserRead(BaseModel):
    id: int
    email: EmailStr
    name: str
    employee_number: str
    role: str
    is_active: bool

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    department: Optional[DepartmentEnum] = None
    phone_number: Optional[str] = None
  