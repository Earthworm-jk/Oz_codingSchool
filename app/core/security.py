from passlib.context import CryptContext

# Bcrypt 알고리즘을 사용하는 암호화 컨텍스트 설정
pwd_context = CryptContext(schemes=["sha256_crypt", "bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    # 72바이트 제한을 방지하기 위해 72자까지만 자릅니다.
    # 비밀번호가 길어도 앞부분 72자만으로도 충분히 안전합니다.
    return pwd_context.hash(password[:72])

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """로그인 시 입력한 비밀번호와 DB의 해시된 비밀번호가 일치하는지 검증"""
    return pwd_context.verify(plain_password, hashed_password)