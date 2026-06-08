from pydantic import ValidationError
from app.schemas.user import UserCreate
import sys
import os

# 현재 파일의 부모 폴더(프로젝트 최상위 경로)를 파이썬이 찾을 수 있도록 등록
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 기존에 있던 코드들 (여기서부터 시작)
from pydantic import ValidationError
from app.schemas.user import UserCreate
# ... 이하 동일
# 테스트용 정상 데이터 예시
valid_data = {
    "employee_number": "20261122",              # 8자리 숫자 (통과)
    "email": "test@hospital.com",
    "password": "SecurePassword123!",           # 대/소문자/숫자/특수문자 포함 (통과)
    "nationality": "korean",
    "first_name": "길동",
    "last_name": "홍",                           # 내국인: 성+이름 필수 (통과)
    "middle_name": None,                        # 내국인: 미들네임 없음 (통과)
    "age": 30,
    "phone_number": "010-1234-5678",
    "gender": "Male",
    "department": "AI-Diagnosis"
}

print("=== 1. 정상 데이터 검증 테스트 ===")
try:
    user = UserCreate(**valid_data)
    print("✅ 성공: 정상 데이터가 스키마를 무사히 통과했습니다!")
    print(f"입력된 유저 이름: {user.last_name}{user.first_name}\n")
except ValidationError as e:
    print("❌ 실패: 정상 데이터인데 에러가 발생했습니다.")
    print(e.json())


print("=== 2. 비즈니스 룰 위반 데이터 검증 테스트 ===")
# 일부러 규칙을 어긴 잘못된 데이터들
invalid_cases = [
    {"field": "사번 오류 (7자리)", "update": {"employee_number": "1234567"}},
    {"field": "비밀번호 오류 (소문자 없음)", "update": {"password": "SECUREPASS123!"}},
    {"field": "내국인 미들네임 오류", "update": {"middle_name": "Danger"}},
    {"field": "내국인 성(last_name) 누락 오류", "update": {"last_name": None}}
]

from fastapi import HTTPException  # 💡 HTTPException을 캐치하기 위해 추가

for case in invalid_cases:
    print(f"👉 테스트 항목: {case['field']}")
    test_data = valid_data.copy()
    test_data.update(case["update"])
    
    try:
        UserCreate(**test_data)
        print("❌ 실패: 잘못된 데이터인데 검증을 통과해버렸습니다!")
    except ValidationError as e:
        error_msg = e.errors()[0]['msg']
        print(f"✅ 성공 (Pydantic 에러 포착): {error_msg}")
    except HTTPException as e:
        # 💡 우리가 utils/validators.py에서 발생시킨 400 에러가 여기로 들어옵니다!
        print(f"✅ 성공 (비즈니스 룰 에러 포착): {e.detail}")
    print("-" * 40)