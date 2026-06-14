import os
import shutil
import tempfile
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
from app.models.patients import Patient
from app.services.redis_prediction_queue import request_pneumonia_prediction

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
    existing_result = await db.execute(
        select(AiAnalysisResult)
        .where(
            AiAnalysisResult.record_id == record_id,
            AiAnalysisResult.ai_model == "SimpleCNN",
        )
        .order_by(AiAnalysisResult.created_at.desc())
        .limit(1)
    )
    existing_analysis = existing_result.scalars().first()
    if existing_analysis:
        existing_analysis.xray_image_url = xray_image.image_url
        record_result = await db.execute(select(MedicalRecord.chart_number).where(MedicalRecord.id == record_id))
        existing_analysis.chart_number = record_result.scalar()
        return existing_analysis

    physical_path = BASE_DIR / xray_image.image_url.lstrip("/")
    prediction_result = await request_pneumonia_prediction(
        physical_path,
        record_id=record_id,
        create_heatmap=True,
    )

    # AI worker 결과 저장
    is_pneumonia = prediction_result["prediction"] == "PNEUMONIA"
    confidence_val = Decimal(f"{prediction_result['confidence'] * 100:.2f}")

    analysis_result = AiAnalysisResult(
        record_id=record_id,
        is_pneumonia=is_pneumonia,
        confidence=confidence_val,
        heatmap_url=prediction_result["heatmap_url"],
        ai_model="SimpleCNN"
    )
    db.add(analysis_result)

    await db.commit()
    await db.refresh(analysis_result)

    # Pydantic schema validation 시 매핑을 위한 임시 속성 주입
    analysis_result.xray_image_url = xray_image.image_url
    record_result = await db.execute(select(MedicalRecord.chart_number).where(MedicalRecord.id == record_id))
    analysis_result.chart_number = record_result.scalar()

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
        prediction_result = await request_pneumonia_prediction(
            temp_file_path,
            create_heatmap=False,
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
    result = await execute_pneumonia_prediction(record_id, xray_image, db)
    return AiAnalysisResultResponse(
        id=result.id,
        record_id=result.record_id,
        is_pneumonia=result.is_pneumonia,
        confidence=result.confidence,
        heatmap_url=result.heatmap_url,
        ai_model=result.ai_model,
        xray_image_url=result.xray_image_url,
        chart_number=result.chart_number,
        created_at=result.created_at,
        updated_at=result.updated_at
    )


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
    result = await execute_pneumonia_prediction(record.id, xray_image, db)
    return AiAnalysisResultResponse(
        id=result.id,
        record_id=result.record_id,
        is_pneumonia=result.is_pneumonia,
        confidence=result.confidence,
        heatmap_url=result.heatmap_url,
        ai_model=result.ai_model,
        xray_image_url=result.xray_image_url,
        chart_number=result.chart_number,
        created_at=result.created_at,
        updated_at=result.updated_at
    )


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
    from sqlalchemy.orm import joinedload, selectinload
    result_query = await db.execute(
        select(AiAnalysisResult)
        .where(AiAnalysisResult.record_id == record_id)
        .options(
            joinedload(AiAnalysisResult.medical_record)
            .selectinload(MedicalRecord.xray_images)
        )
        .order_by(AiAnalysisResult.created_at.desc())
    )
    analysis_results = result_query.scalars().all()
    
    response_list = []
    for a in analysis_results:
        xray_url = None
        if a.medical_record.xray_images and len(a.medical_record.xray_images) > 0:
            xray_url = a.medical_record.xray_images[0].image_url
        response_list.append(AiAnalysisResultResponse(
            id=a.id,
            record_id=a.record_id,
            is_pneumonia=a.is_pneumonia,
            confidence=a.confidence,
            heatmap_url=a.heatmap_url,
            ai_model=a.ai_model,
            xray_image_url=xray_url,
            chart_number=a.medical_record.chart_number,
            created_at=a.created_at,
            updated_at=a.updated_at
        ))
    return response_list


@router.get(
    "/patients/{patient_id}/pneumonia/analyses",
    summary="환자별 전체 AI 폐렴 예측 결과 목록 조회 API",
    response_model=list[AiAnalysisResultResponse]
)
async def get_pneumonia_results_by_patient(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(async_get_db)
):
    # 1. 환자 존재 여부 확인
    patient = await db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="존재하지 않는 환자입니다.")

    # 2. 환자의 전체 진료 기록과 AI 분석 결과를 Left Outer Join하여 조회 (X-Ray가 존재하는 진료 기록만 대상)
    from sqlalchemy.orm import selectinload
    result_query = await db.execute(
        select(MedicalRecord, AiAnalysisResult)
        .join(XrayImage, MedicalRecord.id == XrayImage.record_id)
        .outerjoin(AiAnalysisResult, MedicalRecord.id == AiAnalysisResult.record_id)
        .where(MedicalRecord.patient_id == patient_id)
        .options(
            selectinload(MedicalRecord.xray_images)
        )
        .order_by(MedicalRecord.created_at.desc(), AiAnalysisResult.created_at.desc())
    )
    rows = result_query.all()

    # 3. 각 분석 결과에 xray_image_url과 chart_number 바인딩
    response_list = []
    for medical_record, analysis in rows:
        xray_url = None
        if medical_record.xray_images and len(medical_record.xray_images) > 0:
            xray_url = medical_record.xray_images[0].image_url
            
        if analysis:
            response_list.append(AiAnalysisResultResponse(
                id=analysis.id,
                record_id=analysis.record_id,
                is_pneumonia=analysis.is_pneumonia,
                confidence=analysis.confidence,
                heatmap_url=analysis.heatmap_url,
                ai_model=analysis.ai_model,
                xray_image_url=xray_url,
                chart_number=medical_record.chart_number,
                created_at=analysis.created_at,
                updated_at=analysis.updated_at
            ))
        else:
            response_list.append(AiAnalysisResultResponse(
                id=None,
                record_id=medical_record.id,
                is_pneumonia=None,
                confidence=None,
                heatmap_url=None,
                ai_model=None,
                xray_image_url=xray_url,
                chart_number=medical_record.chart_number,
                created_at=medical_record.created_at,
                updated_at=medical_record.updated_at
            ))

    return response_list



