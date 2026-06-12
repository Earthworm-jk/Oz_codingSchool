from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.auth.jwt import get_current_user
from app.core.db.databases import async_get_db
from app.models.ai_analysis_results import AiAnalysisResult
from app.models.medical_records import MedicalRecord
from app.models.patients import Patient
from app.models.users import User
from app.models.xray_images import XrayImage
from app.schemas.patient_record_schemas import (
    AiAnalysisResultResponse,
    MedicalRecordResponse,
    MedicalRecordUpdateRequest,
    PatientCreateRequest,
    PatientResponse,
    PatientUpdateRequest,
)

router = APIRouter(prefix="/api/v1", tags=["Patient & Medical Records"])

BASE_DIR = Path(__file__).resolve().parent.parent.parent
XRAY_IMAGE_DIR = BASE_DIR / "media" / "xray_images"


def patient_to_response(patient: Patient) -> PatientResponse:
    return PatientResponse(
        id=patient.id,
        name=patient.name,
        age=patient.age,
        gender=patient.gender,
        phone_number=patient.phone,
        created_at=patient.created_at,
        updated_at=patient.updated_at,
    )


def record_to_response(record: MedicalRecord) -> MedicalRecordResponse:
    xray_image = record.xray_images[0] if record.xray_images else None
    return MedicalRecordResponse(
        id=record.id,
        patient_id=record.patient_id,
        chart_number=record.chart_number,
        symptoms=record.symptoms,
        xray_image_url=xray_image.image_url if xray_image else None,
        shooting_datetime=xray_image.shooting_datetime if xray_image else None,
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


async def get_patient_or_404(db: AsyncSession, patient_id: int) -> Patient:
    patient = await db.get(Patient, patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail="존재하지 않는 환자입니다.")
    return patient


async def get_record_or_404(db: AsyncSession, record_id: int) -> MedicalRecord:
    result = await db.execute(
        select(MedicalRecord)
        .where(MedicalRecord.id == record_id)
        .options(selectinload(MedicalRecord.xray_images))
    )
    record = result.scalar_one_or_none()
    if record is None:
        raise HTTPException(status_code=404, detail="존재하지 않는 진료 기록입니다.")
    return record


async def ensure_unique_chart_number(
    db: AsyncSession,
    chart_number: str,
    current_record_id: int | None = None,
) -> None:
    stmt = select(MedicalRecord.id).where(MedicalRecord.chart_number == chart_number)
    if current_record_id is not None:
        stmt = stmt.where(MedicalRecord.id != current_record_id)

    existing_id = await db.scalar(stmt)
    if existing_id is not None:
        raise HTTPException(status_code=400, detail="이미 등록된 차트번호입니다.")


async def save_xray_image(file: UploadFile, record_id: int) -> str:
    if file.content_type and not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="X-Ray 이미지는 이미지 파일만 업로드할 수 있습니다.")

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="X-Ray 이미지 파일이 비어 있습니다.")

    XRAY_IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    suffix = Path(file.filename or "").suffix or ".png"
    filename = f"record_{record_id}_{uuid4().hex}{suffix}"
    file_path = XRAY_IMAGE_DIR / filename
    file_path.write_bytes(contents)
    return f"/media/xray_images/{filename}"


@router.post("/patients", response_model=PatientResponse, summary="환자 등록 API")
async def create_patient_handler(
    body: PatientCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(async_get_db),
):
    patient = Patient(
        name=body.name,
        age=body.age,
        gender=body.gender,
        phone=body.phone_number,
    )
    db.add(patient)
    await db.commit()
    await db.refresh(patient)
    return patient_to_response(patient)


@router.get("/patients", response_model=list[PatientResponse], summary="환자 목록 조회 API")
async def get_patients_handler(
    name: str | None = Query(default=None, description="환자 이름 검색어"),
    gender: str | None = Query(default=None, description="성별 필터"),
    min_age: int | None = Query(default=None, ge=0, description="최소 나이"),
    max_age: int | None = Query(default=None, ge=0, description="최대 나이"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(async_get_db),
):
    stmt = select(Patient).order_by(Patient.id)

    if name:
        stmt = stmt.where(Patient.name.contains(name))
    if gender:
        if gender not in ("male", "female"):
            raise HTTPException(status_code=400, detail="성별은 male 또는 female이어야 합니다.")
        stmt = stmt.where(Patient.gender == gender)
    if min_age is not None:
        stmt = stmt.where(Patient.age >= min_age)
    if max_age is not None:
        stmt = stmt.where(Patient.age <= max_age)
    if min_age is not None and max_age is not None and min_age > max_age:
        raise HTTPException(status_code=400, detail="최소 나이는 최대 나이보다 클 수 없습니다.")

    result = await db.execute(stmt)
    return [patient_to_response(patient) for patient in result.scalars().all()]


@router.get("/patients/{patient_id}", response_model=PatientResponse, summary="환자 상세 조회 API")
async def get_patient_handler(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(async_get_db),
):
    patient = await get_patient_or_404(db, patient_id)
    return patient_to_response(patient)


@router.patch("/patients/{patient_id}", response_model=PatientResponse, summary="환자 정보 수정 API")
async def update_patient_handler(
    patient_id: int,
    body: PatientUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(async_get_db),
):
    update_data = body.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="수정할 정보를 최소 한 개 이상 입력해야 합니다.")

    patient = await get_patient_or_404(db, patient_id)
    if "phone_number" in update_data:
        patient.phone = update_data.pop("phone_number")
    for key, value in update_data.items():
        setattr(patient, key, value)

    await db.commit()
    await db.refresh(patient)
    return patient_to_response(patient)


@router.delete("/patients/{patient_id}", summary="환자 삭제 API")
async def delete_patient_handler(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(async_get_db),
):
    patient = await get_patient_or_404(db, patient_id)
    existing_record_id = await db.scalar(
        select(MedicalRecord.id).where(MedicalRecord.patient_id == patient_id).limit(1)
    )
    if existing_record_id is not None:
        raise HTTPException(status_code=400, detail="진료 기록이 있는 환자는 삭제할 수 없습니다.")

    await db.delete(patient)
    await db.commit()
    return {"message": "환자 정보가 삭제되었습니다."}


@router.post("/medical-records", response_model=MedicalRecordResponse, summary="진료 기록 등록 API")
async def create_medical_record_handler(
    patient_id: int = Form(...),
    chart_number: str = Form(...),
    symptoms: str = Form(...),
    xray_image: UploadFile | None = File(default=None),
    shooting_datetime: datetime | None = Form(default=None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(async_get_db),
):
    await get_patient_or_404(db, patient_id)
    if not chart_number.strip():
        raise HTTPException(status_code=400, detail="차트번호는 필수 입력 항목입니다.")
    if not symptoms.strip():
        raise HTTPException(status_code=400, detail="증상은 필수 입력 항목입니다.")
    await ensure_unique_chart_number(db, chart_number)

    record = MedicalRecord(
        patient_id=patient_id,
        chart_number=chart_number.strip(),
        symptoms=symptoms.strip(),
    )
    db.add(record)
    await db.flush()

    if xray_image is not None:
        image_url = await save_xray_image(xray_image, record.id)
        db.add(
            XrayImage(
                record_id=record.id,
                uploader_id=current_user.id,
                image_url=image_url,
                shooting_datetime=shooting_datetime or datetime.now(UTC),
            )
        )

    await db.commit()
    record = await get_record_or_404(db, record.id)
    return record_to_response(record)


@router.get(
    "/patients/{patient_id}/medical-records",
    response_model=list[MedicalRecordResponse],
    summary="환자별 진료 기록 목록 조회 API",
)
async def get_patient_medical_records_handler(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(async_get_db),
):
    await get_patient_or_404(db, patient_id)
    result = await db.execute(
        select(MedicalRecord)
        .where(MedicalRecord.patient_id == patient_id)
        .options(selectinload(MedicalRecord.xray_images))
        .order_by(MedicalRecord.id.desc())
    )
    return [record_to_response(record) for record in result.scalars().all()]


@router.get(
    "/medical-records/{record_id}",
    response_model=MedicalRecordResponse,
    summary="진료 기록 상세 조회 API",
)
async def get_medical_record_handler(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(async_get_db),
):
    record = await get_record_or_404(db, record_id)
    return record_to_response(record)


@router.patch(
    "/medical-records/{record_id}",
    response_model=MedicalRecordResponse,
    summary="진료 기록 수정 API",
)
async def update_medical_record_handler(
    record_id: int,
    body: MedicalRecordUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(async_get_db),
):
    update_data = body.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="수정할 정보를 최소 한 개 이상 입력해야 합니다.")

    record = await get_record_or_404(db, record_id)
    if "chart_number" in update_data:
        await ensure_unique_chart_number(db, update_data["chart_number"], current_record_id=record_id)

    for key, value in update_data.items():
        setattr(record, key, value)

    await db.commit()
    record = await get_record_or_404(db, record_id)
    return record_to_response(record)


@router.get(
    "/medical-records/{record_id}/analyses",
    response_model=list[AiAnalysisResultResponse],
    summary="진료 기록별 AI 분석 결과 목록 조회 API",
)
async def get_medical_record_analyses_handler(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(async_get_db),
):
    await get_record_or_404(db, record_id)
    result = await db.execute(
        select(AiAnalysisResult)
        .where(AiAnalysisResult.record_id == record_id)
        .order_by(AiAnalysisResult.id.desc())
    )
    return result.scalars().all()
