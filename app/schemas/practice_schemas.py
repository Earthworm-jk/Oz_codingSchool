from pydantic import BaseModel, Field

# 회원 등록 요청 바디
class UserCreateRequest(BaseModel):
    nationality: str
    last_name: str | None = None
    first_name: str
    middle_name: str | None = None
    age: int
    email: str
    password: str
    employee_number: str


# 회원 정보 수정 요청 바디
class UserUpdateRequest(BaseModel):
    age: int | None = Field(default=None, description="수정할 나이 (최소 14세)")
    email: str | None = Field(default=None, description="수정할 이메일 (최대 30자)")
    password: str | None = Field(default=None, description="수정할 비밀번호 (대소문자, 특수문자가 각 1개씩 필수, 최소 8자, 최대 20자)")
    nationality: str | None = Field(default=None, description="수정할 국적 (korean 또는 foreigner)")
    last_name: str | None = Field(default=None, description="수정할 성")
    first_name: str | None = Field(default=None, description="수정할 이름")
    middle_name: str | None = Field(default=None, description="수정할 미들네임")


# 회원 응답 바디 (비밀번호 제외)
class UserResponse(BaseModel):
    id: int
    nationality: str
    last_name: str | None = None
    first_name: str
    middle_name: str | None = None
    age: int
    email: str
    employee_number: str
