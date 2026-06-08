import os
from pathlib import Path

from fastapi import FastAPI
from starlette.staticfiles import StaticFiles
from starlette.responses import FileResponse

# 💡 async_engine 정확하게 임포트
from app.core.db.databases import Base, async_engine 
from app.apis.v1 import user as user_v1
from app.apis.practice_apis import router as practice_router

# 💡 FastAPI의 lifespan(수명 주기) 이벤트 기능을 활용한 안전한 비동기 테이블 생성
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
# [서버 시작 시]
    # 테이블 생성은 더 이상 여기서 하지 않습니다! (Alembic이 처리함)
    # 대신 DB 연결이 정상인지 확인하거나, 필수 데이터를 초기에 넣는 작업만 수행하세요.
    print("서버 시작: 데이터베이스 연결 확인 중...")
    
    yield
    
    # [서버 종료 시]
    print("서버 종료: 정리 작업 수행 중...")
    
app = FastAPI(
    title="Chest X-Ray AI Diagnosis Service",
    description="프론트엔드 정적 파일 서빙 및 실전용 User API가 결합된 통합 서버입니다.",
    version="1.0.0",
    lifespan=lifespan  # 💡 lifespan 이벤트 등록
)

# 💡 실전용 v1 유저 라우터를 /api/v1/users/signup 경로로 등록
app.include_router(user_v1.router, prefix="/api/v1")

# 기존 연습용 라우터도 유지
app.include_router(practice_router)

BASE_DIR = Path(__file__).resolve().parent.parent

# 만약 static, media 폴더가 존재하지 않으면 생성 (기존 유지)
if not (BASE_DIR / "static").exists():
    os.mkdir(BASE_DIR / "static")
if not (BASE_DIR / "media").exists():
    os.mkdir(BASE_DIR / "media")

# 정적 파일 마운트 (기존 유지)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
app.mount("/media", StaticFiles(directory=BASE_DIR / "media"), name="media")


@app.get(path="/healthcheck", status_code=200, include_in_schema=False)
async def healthcheck():
    return {"status": "ok"}


@app.get("/", include_in_schema=False)
async def index():
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.get("/{path:path}", include_in_schema=False)
async def catch_all(path: str):
    if (
        path.startswith("api/v1")
        or path.startswith("static/")
        or path.startswith("media/")
    ):
        from fastapi import HTTPException
        raise HTTPException(status_code=404)
    return FileResponse(BASE_DIR / "static" / "index.html")