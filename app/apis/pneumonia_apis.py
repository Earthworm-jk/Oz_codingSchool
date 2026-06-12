import os
import shutil
import tempfile
import uuid
from pathlib import Path
from contextlib import contextmanager
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from decimal import Decimal

from app.core.db.databases import async_get_db
from app.models.medical_records import MedicalRecord
from app.models.xray_images import XrayImage
from app.models.ai_analysis_results import AiAnalysisResult
from app.schemas.pneumonia_schemas import PneumoniaPredictionResponse
from app.schemas.patient_record_schemas import AiAnalysisResultResponse
from app.core.auth.jwt import get_current_user
from app.models.users import User
from worker.model import predict_pneumonia, generate_heatmap

router = APIRouter(prefix="/api/v1", tags=["AI Pneumonia Prediction"])
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # 프로젝트 루트 디렉토리


# ==========================================
# 헬퍼 함수 및 컨텍스트 매니저 (try-except 추상화)
# ==========================================

@contextmanager
def temp_upload_file(file: UploadFile):
    """임시 파일의 저장 및 자동 삭제(Cleanup)를 담당하는 컨텍스트 매니저"""
    ext = os.path.splitext(file.filename)[1].lower()
    temp_dir = BASE_DIR / "media" / "temp"
    os.makedirs(temp_dir, exist_ok=True)

    # 윈도우 파일 잠금 문제를 방지하기 위해 생성 후 즉시 닫고 파일명을 확보합니다.
    temp_file = tempfile.NamedTemporaryFile(dir=temp_dir, suffix=ext, delete=False)
    temp_path = Path(temp_file.name)
    temp_file.close()

    try:
        with open(temp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        if temp_path.stat().st_size == 0:
            raise HTTPException(status_code=400, detail="비어 있는 파일입니다.")
        yield temp_path
    finally:
        if temp_path.exists():
            os.remove(temp_path)


def safe_predict_pneumonia(image_path: str, error_msg: str = "AI 분석 중 오류가 발생했습니다") -> dict:
    """예측 시 발생하는 일반 예외를 HTTPException 500으로 자동 변환해주는 헬퍼"""
    try:
        return predict_pneumonia(image_path)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{error_msg}: {str(e)}")


def safe_copy_file(src: Path, dst: Path):
    """실패해도 프로그램 흐름에 지장을 주지 않는 파일 복사용 헬퍼"""
    try:
        shutil.copy(src, dst)
    except Exception:
        pass


# ==========================================
# 의존성 주입 (Dependencies)
# ==========================================

async def get_valid_medical_record(
    record_id: int,
    db: AsyncSession = Depends(async_get_db)
) -> MedicalRecord:
    record_result = await db.execute(select(MedicalRecord).where(MedicalRecord.id == record_id))
    record = record_result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="진료 기록 ID가 존재하지 않습니다.")
    return record


async def get_valid_xray_image_from_record(
    record: MedicalRecord,
    db: AsyncSession
) -> XrayImage:
    xray_result = await db.execute(
        select(XrayImage).where(XrayImage.record_id == record.id).order_by(XrayImage.id.desc())
    )
    xray_image = xray_result.scalars().first()
    if not xray_image:
        raise HTTPException(status_code=404, detail="진료 기록에 등록된 X-Ray 이미지가 없습니다.")

    image_url = xray_image.image_url
    relative_path = image_url.lstrip("/")
    physical_path = BASE_DIR / relative_path

    if not physical_path.exists() or not physical_path.is_file():
        raise HTTPException(status_code=404, detail=f"X-Ray 이미지 파일이 서버에 존재하지 않습니다. (경로: {relative_path})")

    return xray_image


async def get_valid_xray_image(
    record: MedicalRecord = Depends(get_valid_medical_record),
    db: AsyncSession = Depends(async_get_db)
) -> XrayImage:
    return await get_valid_xray_image_from_record(record, db)


async def execute_pneumonia_prediction(
    record_id: int,
    xray_image: XrayImage,
    db: AsyncSession
) -> AiAnalysisResult:
    physical_path = BASE_DIR / xray_image.image_url.lstrip("/")

    # 1. 모델 예측 수행
    prediction_result = safe_predict_pneumonia(str(physical_path))

    # 2. 결과 저장
    is_pneumonia = prediction_result["prediction"] == "PNEUMONIA"
    confidence_val = Decimal(f"{prediction_result['confidence'] * 100:.2f}")

    # Heatmap 생성 및 저장 (Grad-CAM 렌더링)
    heatmap_dir = BASE_DIR / "media" / "heatmap"
    os.makedirs(heatmap_dir, exist_ok=True)
    
    unique_suffix = uuid.uuid4().hex[:8]
    heatmap_filename = f"record_{record_id}_{unique_suffix}.png"
    heatmap_path = heatmap_dir / heatmap_filename
    
    try:
        generate_heatmap(str(physical_path), str(heatmap_path))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"히트맵 생성에 실패했습니다. (사유: {str(e)})"
        )
    
    heatmap_url = f"/media/heatmap/{heatmap_filename}"

    analysis_result = AiAnalysisResult(
        record_id=record_id,
        is_pneumonia=is_pneumonia,
        confidence=confidence_val,
        heatmap_url=heatmap_url,
        ai_model="SimpleCNN"
    )
    db.add(analysis_result)

    await db.commit()
    await db.refresh(analysis_result)
    return analysis_result


# ==========================================
# API 엔드포인트 핸들러
# ==========================================

@router.post(
    "/pneumonia/predict/upload",
    summary="AI 폐렴 즉시 예측 API (업로드)",
    response_model=PneumoniaPredictionResponse
)
async def predict_pneumonia_by_upload(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    # 1. 포맷 확인
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in [".png", ".jpg", ".jpeg"]:
        raise HTTPException(status_code=400, detail="지원되지 않는 이미지 포맷입니다. (PNG, JPG, JPEG만 허용)")

    # 2. 임시 파일 구동 및 예측
    with temp_upload_file(file) as temp_file_path:
        prediction_result = safe_predict_pneumonia(
            str(temp_file_path),
            error_msg="이미지 분석 중 에러가 발생했습니다"
        )

    return {
        "prediction": prediction_result["prediction"],
        "confidence": prediction_result["confidence"] * 100,
        "probability_normal": prediction_result["probability_normal"] * 100,
        "probability_pneumonia": prediction_result["probability_pneumonia"] * 100
    }


@router.post(
    "/medical-records/{record_id}/predict",
    summary="AI 폐렴 예측 실행 API",
    response_model=AiAnalysisResultResponse
)
async def predict_pneumonia_by_record(
    record_id: int,
    xray_image: XrayImage = Depends(get_valid_xray_image),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(async_get_db)
):
    return await execute_pneumonia_prediction(record_id, xray_image, db)


@router.post(
    "/pneumonia/predict",
    summary="AI 폐렴 예측 실행 API (ID 또는 Patient ID 기반)",
    response_model=AiAnalysisResultResponse
)
async def predict_pneumonia_api(
    record_id: int | None = Query(None, description="진료 기록 ID"),
    patient_id: int | None = Query(None, description="환자 ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(async_get_db)
):
    if record_id is None and patient_id is None:
        raise HTTPException(status_code=400, detail="record_id 또는 patient_id 중 하나는 필수입니다.")
    
    if record_id is not None:
        record = await get_valid_medical_record(record_id, db)
    else:
        # patient_id 기반으로 가장 최근의 진료 기록을 조회
        record_result = await db.execute(
            select(MedicalRecord)
            .where(MedicalRecord.patient_id == patient_id)
            .order_by(MedicalRecord.id.desc())
            .limit(1)
        )
        record = record_result.scalar_one_or_none()
        if not record:
            raise HTTPException(status_code=404, detail="해당 환자의 진료 기록이 존재하지 않습니다.")
    
    xray_image = await get_valid_xray_image_from_record(record, db)
    return await execute_pneumonia_prediction(record.id, xray_image, db)


@router.get(
    "/medical-records/{record_id}/analyses",
    summary="AI 폐렴 예측 결과 조회 API",
    response_model=list[AiAnalysisResultResponse]
)
async def get_pneumonia_result_by_record(
    record_id: int,
    record: MedicalRecord = Depends(get_valid_medical_record),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(async_get_db)
):
    result_query = await db.execute(
        select(AiAnalysisResult)
        .where(AiAnalysisResult.record_id == record_id)
        .order_by(AiAnalysisResult.created_at.desc())
    )
    analysis_results = result_query.scalars().all()
    return analysis_results
