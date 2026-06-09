import re
from fastapi import HTTPException

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

def validate_nationality_names(nationality: str, first_name: str, last_name: str | None, middle_name: str | None):
    if nationality == "korean":
        if not last_name or not first_name:
            raise HTTPException(status_code=400, detail="내국인은 성과 이름이 필수입니다.")
        combined_len = len(last_name.strip()) + len(first_name.strip())
        if not (2 <= combined_len <= 10):
            raise HTTPException(status_code=400, detail="내국인 성명 길이는 2~10자여야 합니다.")
        if middle_name and middle_name.strip():
            raise HTTPException(status_code=400, detail="내국인은 미들네임 불가입니다.")
    else: # foreigner
        if not first_name:
            raise HTTPException(status_code=400, detail="외국인 이름은 필수입니다.")
        # 기타 길이 검증은 기존 로직대로 유지...

def validate_password(password: str):
    if not (8 <= len(password) <= 20) or \
       not any(c.isupper() for c in password) or \
       not any(c.islower() for c in password) or \
       not any(c.isdigit() for c in password) or \
       not re.search(r"[!@#$%^&*(),.?\":{}|<>\-_+=\[\]\\/;`~']", password):
        raise HTTPException(status_code=400, detail="비밀번호 형식(8~20자, 대/소문자, 숫자, 특수문자 포함)을 확인하세요.")