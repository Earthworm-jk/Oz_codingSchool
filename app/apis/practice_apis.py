# app/apis/practice_apis.py
import re
from typing import List
# pyrefly: ignore [missing-import]
from fastapi import APIRouter, HTTPException, Path
from app.schemas.practice_schemas import UserCreateRequest, UserResponse, UserUpdateRequest

# 1. 우리들만의 작은 라우터(표지판)를 생성합니다.
# prefix를 "/practice_api"로 지정하여 요구사항의 endpoint 경로를 맞춥니다.
router = APIRouter(prefix="/practice_api", tags=["Practice API"])

# 초기 회원 목록
user_list = [
    {
        "id": 1,
        "nationality": "korean",
        "last_name": "홍",
        "first_name": "길동",
        "middle_name": None,
        "age": 24,
        "email": "gildong24@example.com",
        "password": "Password1234!!",
        "employee_number": "20240001"
    },
    {
        "id": 2,
        "nationality": "korean",
        "last_name": "장",
        "first_name": "문복",
        "middle_name": None,
        "age": 21,
        "email": "moonluck12@example.com",
        "password": "Check1321!",
        "employee_number": "20240002"
    },
    {
        "id": 3,
        "nationality": "korean",
        "last_name": "임",
        "first_name": "우진",
        "middle_name": None,
        "age": 31,
        "email": "limousine33@example.com",
        "password": "lwsPAssword12@",
        "employee_number": "20240003"
    }
]

# --- Pydantic 요청/응답 스키마 정의 ---
# app/schemas/practice_schemas.py 파일로 분리하여 위에서 import 하였습니다.



# --- 입력값 검증용 Helper 함수 정의 ---

# 이메일 형식을 체크하기 위한 정규표현식
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

def validate_nationality_names(nationality: str, first_name: str, last_name: str | None, middle_name: str | None):
    if nationality not in ("korean", "foreigner"):
        raise HTTPException(status_code=400, detail="국적 구분은 korean(내국인) 또는 foreigner(외국인)이어야 합니다.")
    
    if nationality == "korean":
        # 내국인: 성 필수, 이름 필수
        if not last_name or not last_name.strip():
            raise HTTPException(status_code=400, detail="내국인은 성(last_name)이 필수입니다.")
        if not first_name or not first_name.strip():
            raise HTTPException(status_code=400, detail="내국인은 이름(first_name)이 필수입니다.")
        
        # 이름 길이 제한 (기존 이름 길이 제한 2~10글자 맞춤: 성 + 이름 결합 길이)
        combined_len = len(last_name.strip()) + len(first_name.strip())
        if combined_len < 2 or combined_len > 10:
            raise HTTPException(status_code=400, detail="내국인 성명의 총 길이는 최소 2글자 이상, 최대 10글자 이하여야 합니다.")
            
        if middle_name and middle_name.strip():
            raise HTTPException(status_code=400, detail="내국인은 미들네임(middle_name)을 입력할 수 없습니다.")
    else:
        # 외국인: 성 선택(필수 아님), 이름 필수, 미들네임 선택 가능
        if not first_name or not first_name.strip():
            raise HTTPException(status_code=400, detail="외국인은 이름(first_name)이 필수입니다.")
        
        if len(first_name.strip()) < 1 or len(first_name.strip()) > 20:
            raise HTTPException(status_code=400, detail="외국인 이름(first_name)은 최소 1자 이상, 최대 20글자 이하여야 합니다.")
            
        if last_name and len(last_name.strip()) > 20:
            raise HTTPException(status_code=400, detail="외국인 성(last_name)은 최대 20글자 이하여야 합니다.")
            
        if middle_name and len(middle_name.strip()) > 20:
            raise HTTPException(status_code=400, detail="외국인 미들네임(middle_name)은 최대 20글자 이하여야 합니다.")

def validate_age(age: int):
    if age is None:
        raise HTTPException(status_code=400, detail="나이는 필수 입력 항목입니다.")
    # 나이는 최소 14세 이상
    if age < 14:
        raise HTTPException(status_code=400, detail="나이는 최소 14세 이상이어야 합니다.")

def validate_email(email: str, current_user_id: int = None):
    if email is None:
        raise HTTPException(status_code=400, detail="이메일은 필수 입력 항목입니다.")
    # email 형식 정규표현식 검증
    if not EMAIL_REGEX.match(email):
        raise HTTPException(status_code=400, detail="올바른 이메일 형식이 아닙니다.")
    # 최대 30자
    if len(email) > 30:
        raise HTTPException(status_code=400, detail="이메일은 최대 30자 이하여야 합니다.")
    # 중복 불가능 검증 (수정 시 본인의 기존 이메일은 제외)
    for u in user_list:
        if u["email"] == email and (current_user_id is None or u["id"] != current_user_id):
            raise HTTPException(status_code=400, detail="이미 등록된 이메일입니다.")

def validate_password(password: str):
    if password is None:
        raise HTTPException(status_code=400, detail="비밀번호는 필수 입력 항목입니다.")
    # 최소 8자 이상, 최대 20자 이하
    if len(password) < 8 or len(password) > 20:
        raise HTTPException(status_code=400, detail="비밀번호는 최소 8자 이상, 최대 20자 이하여야 합니다.")
    # 대소문자, 특수문자, 숫자가 각 1개씩 필수 포함
    if not any(c.isupper() for c in password):
        raise HTTPException(status_code=400, detail="비밀번호에는 최소 1개 이상의 대문자가 포함되어야 합니다.")
    if not any(c.islower() for c in password):
        raise HTTPException(status_code=400, detail="비밀번호에는 최소 1개 이상의 소문자가 포함되어야 합니다.")
    if not any(c.isdigit() for c in password):
        raise HTTPException(status_code=400, detail="비밀번호에는 최소 1개 이상의 숫자가 포함되어야 합니다.")
    
    # 특수문자 정규식 체크
    special_chars = re.compile(r"[!@#$%^&*(),.?\":{}|<>\-_+=\[\]\\/;`~']")
    if not special_chars.search(password):
        raise HTTPException(status_code=400, detail="비밀번호에는 최소 1개 이상의 특수문자가 포함되어야 합니다.")

def validate_employee_number(employee_number: str):
    # 사번 형식 검증 (8자리 숫자 예: 20240001)
    if not re.match(r"^\d{8}$", employee_number):
        raise HTTPException(status_code=400, detail="사번은 8자리 숫자여야 합니다.")
    # 중복 가입 방지를 위한 사번 중복 검사
    for u in user_list:
        if u.get("employee_number") == employee_number:
            raise HTTPException(status_code=400, detail="이미 가입된 사번입니다.")




# --- API Endpoint 구현 ---

@router.get(
    "/users/check-email",
    summary="이메일 중복 확인 API"
)
def check_email_handler(email: str):
    # 이메일 형식 및 길이 검증
    if not EMAIL_REGEX.match(email):
        raise HTTPException(status_code=400, detail="올바른 이메일 형식이 아닙니다.")
    if len(email) > 30:
        raise HTTPException(status_code=400, detail="이메일은 최대 30자 이하여야 합니다.")
    
    # 중복 여부 확인
    for u in user_list:
        if u["email"] == email:
            raise HTTPException(status_code=400, detail="이미 등록된 이메일입니다.")
            
    return {"message": "사용 가능한 이메일입니다."}


@router.get(
    "/users",
    summary="전체 회원 목록 조회 API",
    response_model=List[UserResponse]
)
def get_users_handler():
    # 전체 회원의 정보를 목록으로 조회하되 password 필드는 response_model에 의해 제외됨
    return user_list


@router.get(
    "/users/{user_id}",
    summary="단일 회원 상세 조회 API",
    response_model=UserResponse
)
def get_user_handler(
    user_id: int = Path(..., description="조회할 회원의 고유 ID")
):
    # 특정 회원 상세 조회
    for u in user_list:
        if u["id"] == user_id:
            return u
    # 유효한 id가 아닌 경우 404 에러 응답
    raise HTTPException(status_code=404, detail="존재하지 않는 회원 ID입니다.")


@router.post(
    "/users",
    summary="새로운 회원 추가 API",
    response_model=UserResponse
)
def create_user_handler(body: UserCreateRequest):
    # 입력값 검증 수행
    validate_nationality_names(body.nationality, body.first_name, body.last_name, body.middle_name)
    validate_age(body.age)
    validate_email(body.email)
    validate_password(body.password)
    validate_employee_number(body.employee_number)

    # 신규 회원 ID 생성 (가장 큰 ID + 1, 리스트가 비어있으면 1)
    new_id = max((u["id"] for u in user_list), default=0) + 1

    new_user = {
        "id": new_id,
        "nationality": body.nationality,
        "last_name": body.last_name,
        "first_name": body.first_name,
        "middle_name": body.middle_name,
        "age": body.age,
        "email": body.email,
        "password": body.password,
        "employee_number": body.employee_number
    }
    user_list.append(new_user)
    return new_user


@router.patch(
    "/users/{user_id}",
    summary="회원 정보 수정 API",
    response_model=UserResponse
)
def update_user_handler(
    body: UserUpdateRequest,
    user_id: int = Path(..., description="수정할 회원의 고유 ID")
):
    # 모든 항목이 입력되지 않은 경우 400 Bad Request
    update_data = body.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="수정할 정보를 최소 한 개 이상 입력해야 합니다.")

    # 회원 ID 조회
    target_user = None
    for u in user_list:
        if u["id"] == user_id:
            target_user = u
            break

    if not target_user:
        raise HTTPException(status_code=404, detail="존재하지 않는 회원 ID입니다.")

    # 임시 검증을 위해 기존 사용자 정보와 입력값 병합
    temp_user = target_user.copy()
    for key, value in update_data.items():
        temp_user[key] = value

    # 1. 국적 및 이름 결합 검증
    name_fields = {"nationality", "first_name", "last_name", "middle_name"}
    if any(field in update_data for field in name_fields):
        validate_nationality_names(
            temp_user["nationality"],
            temp_user["first_name"],
            temp_user["last_name"],
            temp_user["middle_name"]
        )

    # 2. 나이 검증
    if "age" in update_data:
        validate_age(update_data["age"])

    # 3. 이메일 검증
    if "email" in update_data:
        validate_email(update_data["email"], current_user_id=user_id)

    # 4. 비밀번호 검증
    if "password" in update_data:
        validate_password(update_data["password"])

    # 모든 검증을 통과했으므로 실제 데이터 반영
    for key, value in update_data.items():
        target_user[key] = value

    return target_user


@router.delete(
    "/users/{user_id}",
    summary="회원 정보 삭제 API"
)
def delete_user_handler(
    user_id: int = Path(..., description="삭제할 회원의 고유 ID")
):
    # 회원 ID 조회 및 삭제
    for i, u in enumerate(user_list):
        if u["id"] == user_id:
            del user_list[i]
            return {"message": "회원 정보가 삭제되었습니다."}

    # 유효하지 않은 ID인 경우 404 Not Found
    raise HTTPException(status_code=404, detail="존재하지 않는 회원 ID입니다.")