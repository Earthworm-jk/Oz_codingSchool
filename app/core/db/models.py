import uuid as uuid_pkg
from datetime import UTC, datetime
from typing import List, Optional

from app.core.db.databases import Base
from sqlalchemy import Boolean, DateTime, text, String, Text, ForeignKey, Integer
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid6 import uuid7

# --- [공통 뼈대 믹스인] ---
class UUIDMixin:
    # ERD의 id (bigint/integer) 대신 프로젝트 기본 규격인 UUID7 (CHAR(36)) 사용
    id: Mapped[uuid_pkg.UUID] = mapped_column(
        CHAR(36), primary_key=True, default=uuid7
    )

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC), server_default=text("current_timestamp")
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, onupdate=lambda: datetime.now(UTC), server_default=text("current_timestamp")
    )

class SoftDeleteMixin:
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)


# ==================================================
# 💡 ERD 기반 실제 모델(테이블) 정의
# ==================================================

class User(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(20), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    gender: Mapped[str] = mapped_column(String(10), nullable=False)  # 임시 String 처리 (Male/Female 등)
    department: Mapped[str] = mapped_column(String(50), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # 관계 정의 (XrayImage 업로더 관계)
    uploaded_xrays: Mapped[List["XrayImage"]] = relationship("XrayImage", back_populates="uploader")


class Patient(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "patients"

    name: Mapped[str] = mapped_column(String(30), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    gender: Mapped[str] = mapped_column(String(10), nullable=False)
    phone: Mapped[str] = mapped_column(String(11), nullable=False)

    # 관계 정의
    medical_records: Mapped[List["MedicalRecord"]] = relationship("MedicalRecord", back_populates="patient")


class MedicalRecord(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "medical_records"

    patient_id: Mapped[uuid_pkg.UUID] = mapped_column(CHAR(36), ForeignKey("patients.id"), nullable=False)
    chart_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    symptoms: Mapped[str] = mapped_column(Text, nullable=False)

    # 관계 정의
    patient: Mapped["Patient"] = relationship("Patient", back_populates="medical_records")
    xray_images: Mapped[List["XrayImage"]] = relationship("XrayImage", back_populates="medical_record")
    ai_results: Mapped[List["AIAnalysisResult"]] = relationship("AIAnalysisResult", back_populates="medical_record")


class XrayImage(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "xray_images"

    record_id: Mapped[uuid_pkg.UUID] = mapped_column(CHAR(36), ForeignKey("medical_records.id"), nullable=False)
    uploader_id: Mapped[uuid_pkg.UUID] = mapped_column(CHAR(36), ForeignKey("users.id"), nullable=False)
    image_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    shooting_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # 관계 정의
    medical_record: Mapped["MedicalRecord"] = relationship("MedicalRecord", back_populates="xray_images")
    uploader: Mapped["User"] = relationship("User", back_populates="uploaded_xrays")


class AIAnalysisResult(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "ai_analysis_results"

    record_id: Mapped[uuid_pkg.UUID] = mapped_column(CHAR(36), ForeignKey("medical_records.id"), nullable=False)
    is_pneumonia: Mapped[bool] = mapped_column(Boolean, nullable=False)
    confidence: Mapped[float] = mapped_column(nullable=False)  # float(Real) 처리
    heatmap_url: Mapped[str] = mapped_column(String(255), nullable=False)
    ai_model: Mapped[str] = mapped_column(String(50), nullable=False)

    # 관계 정의
    medical_record: Mapped["MedicalRecord"] = relationship("MedicalRecord", back_populates="ai_results")
