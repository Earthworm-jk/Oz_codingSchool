import re
from fastapi import HTTPException, status

def validate_employee_number(employee_number: str) -> str:
    """
    사번 포맷 검증 (무조건 8자리 숫자)
    """
    if not employee_number:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="사번은 필수 입력 항목입니다."
        )
    
    # 정규표현식으로 정확히 8자리 숫자 모양인지 확인
    if not re.match(r"^\d{8}$", employee_number):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="사번은 무조건 8자리 숫자 형식이어야 합니다. (예: 20260101)"
        )
    return employee_number


def validate_password(password: str) -> str:
    """
    비밀번호 복잡도 검증
    - 8~20자 사이
    - 대문자, 소문자, 숫자, 특수문자 각각 최소 1개 이상 포함
    """
    if not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="비밀번호는 필수 입력 항목입니다."
        )

    if not (8 <= len(password) <= 20):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="비밀번호는 8자 이상 20자 이하여야 합니다."
        )
    
    if not re.search(r"[A-Z]", password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="비밀번호에 대문자가 최소 1개 이상 포함되어야 합니다."
        )
    if not re.search(r"[a-z]", password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="비밀번호에 소문자가 최소 1개 이상 포함되어야 합니다."
        )
    if not re.search(r"\d", password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="비밀번호에 숫자가 최소 1개 이상 포함되어야 합니다."
        )
    # 기획서에 명시된 일반적인 특수문자 패턴 검사
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>_+-]", password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="비밀번호에 특수문자가 최소 1개 이상 포함되어야 합니다."
        )
    return password


def validate_nationality_names(nationality: str, first_name: str, last_name: str = None, middle_name: str = None):
    """
    국적별 성명 제약 조건 검증
    - 내국인(korean): 성과 이름 필수, 미들네임 불가, 공백 제외 총 길이 2~10자
    - 외국인(foreigner): 이름 필수(1~20자), 성과 미들네임 선택(입력 시 최대 20자)
    """
    # 입력값 양끝 공백 제거 정리
    first_name = first_name.strip() if first_name else ""
    last_name = last_name.strip() if last_name else None
    middle_name = middle_name.strip() if middle_name else None

    if nationality == "korean":
        if not last_name or not first_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="내국인은 성(last_name)과 이름(first_name)이 모두 필수입니다."
            )
        if middle_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="내국인은 미들네임(middle_name)을 입력할 수 없습니다."
            )
        
        # 성 + 이름 공백 제외 결합 길이 체크
        full_name_len = len(last_name + first_name)
        if not (2 <= full_name_len <= 10):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="내국인의 성+이름 길이는 공백을 제외하고 2자 이상 10자 이하여야 합니다."
            )
            
    elif nationality == "foreigner":
        if not first_name or not (1 <= len(first_name) <= 20):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="외국인은 이름(first_name)이 필수이며, 1자 이상 20자 이하여야 합니다."
            )
        if last_name and len(last_name) > 20:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="외국인의 성(last_name)은 최대 20자까지 가능합니다."
            )
        if middle_name and len(middle_name) > 20:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="외국인의 미들네임(middle_name)은 최대 20자까지 가능합니다."
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="올바르지 않은 국적 형식입니다. 'korean' 또는 'foreigner'여야 합니다."
        )


def validate_age(age: int | None) -> int | None:
    """
    나이 유효성 검증 (선택 사항이지만 입력 시 정상 범위 검사)
    """
    if age is not None:
        if age < 0 or age > 150:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="나이는 0세부터 150세 사이의 올바른 값이어야 합니다."
            )
    return age