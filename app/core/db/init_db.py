import sys
import os
import asyncio

# [경로 보정] 파이썬 탐색 경로에 프로젝트 루트 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# SQLite 비동기 엔진을 직접 선언 (MySQL 간섭 차단)
from sqlalchemy.ext.asyncio import create_async_engine
DATABASE_URL = "sqlite+aiosqlite:///./test.db"
sqlite_engine = create_async_engine(DATABASE_URL, echo=True, future=True)

async def create_sqlite_db():
    print("\n==================================================")
    print("🚀 SQLite 데이터베이스 및 테이블 생성을 시작합니다.")
    print("==================================================")

    # 1. models.py를 읽어와 Base에 테이블 등록
    try:
        from app.core.db import models
        from app.core.db.databases import Base
        print("✅ models.py 테이블 구조 로드 완료!")
    except ImportError as e:
        print(f"❌ 데이터 로드 실패: {e}")
        return

    # 2. 감지된 테이블 목록 확인
    detected_tables = list(Base.metadata.tables.keys())
    print(f"▶ 생성될 테이블 목록: {detected_tables}")
    
    if not detected_tables:
        print("⚠ 감지된 테이블이 없습니다. models.py의 클래스들을 확인해 주세요.")
        return

    # 3. SQLite 파일 및 테이블 생성 실행
    print("\n[SQLite 파일 및 테이블 빌드 중...]")
    try:
        async with sqlite_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("\n✨ test.db 파일과 모든 테이블이 성공적으로 생성되었습니다!")
    except Exception as e:
        print(f"❌ 빌드 중 오류 발생: {e}")
    finally:
        await sqlite_engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_sqlite_db())