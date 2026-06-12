import re
from fastapi import HTTPException

# 이메일, 사번 정규식 정의
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
EMP_REGEX = re.compile(r"^\d{8}$")

def validate_nationality_names(nationality: str, first_name: str, last_name: str | None, middle_name: str | None):
    # 1. 국적 값 오타 방지
    if nationality not in ("korean", "foreigner"):
        raise HTTPException(status_code=400, detail="국적은 korean 또는 foreigner만 가능합니다.")
    
    # 2. 공통 이름 길이 검증 (공백 제거 후)
    fn = (first_name or "").strip()
    ln = (last_name or "").strip()
    mn = (middle_name or "").strip()

    if nationality == "korean":
        if not ln or not fn:
            raise HTTPException(status_code=400, detail="내국인은 성과 이름이 필수입니다.")
        # 성+이름 길이 검증
        if not (2 <= len(ln) + len(fn) <= 10):
            raise HTTPException(status_code=400, detail="내국인 성명 길이는 2~10자여야 합니다.")
        if mn:
            raise HTTPException(status_code=400, detail="내국인은 미들네임을 사용할 수 없습니다.")
    else: # foreigner
        if not fn:
            raise HTTPException(status_code=400, detail="외국인은 이름이 필수입니다.")
        # 각 필드별 최대 길이 제한 (DB 컬럼 사이즈 고려)
        if len(fn) > 20 or len(ln) > 20 or len(mn) > 20:
            raise HTTPException(status_code=400, detail="이름 관련 필드는 최대 20자까지 가능합니다.")

def validate_password(password: str):
    # 길이 검증
    if not (8 <= len(password) <= 20):
        raise HTTPException(status_code=400, detail="비밀번호는 8~20자여야 합니다.")
    
    # 필수 포함 요소 검증
    if not (any(c.isupper() for c in password) and 
            any(c.islower() for c in password) and 
            any(c.isdigit() for c in password) and 
            re.search(r"[!@#$%^&*(),.?\":{}|<>\-_+=\[\]\\/;`~']", password)):
        raise HTTPException(status_code=400, detail="비밀번호는 대/소문자, 숫자, 특수문자를 모두 포함해야 합니다.")

def validate_employee_number(employee_number: str):
    # 1. 영어가 포함되어 있는지 먼저 체크 (더 직관적인 에러 제공)
    if re.search(r'[a-zA-Z]', employee_number):
        raise HTTPException(status_code=400, detail="사번에는 영문을 포함할 수 없습니다.")
    
    # 2. 8자리 숫자인지 체크
    if not re.match(r"^\d{8}$", employee_number):
        raise HTTPException(status_code=400, detail="사번은 정확히 8자리 숫자여야 합니다.")