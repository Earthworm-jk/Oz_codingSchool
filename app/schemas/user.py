from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str = Field(..., max_length=20)
    last_name: Optional[str] = Field(None, max_length=20)
    middle_name: Optional[str] = Field(None, max_length=20)
    employee_number: str
    phone_number: str
    nationality: str
    gender: str
    department: str

class UserRead(BaseModel):
    id: int
    email: EmailStr
    name: str
    employee_number: str
    role: str
    is_active: bool

    class Config:
        from_attributes = True