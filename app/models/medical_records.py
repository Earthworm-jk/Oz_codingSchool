from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy import BigInteger, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.databases import Base
from app.core.db.models import TimestampMixin

# TYPE_CHECKING 블록 내에서만 임포트합니다.
if TYPE_CHECKING:
    from app.models.patients import Patient
    from app.models.xray_images import XrayImage
    from app.models.ai_analysis_results import AiAnalysisResult

class MedicalRecord(Base, TimestampMixin):
    __tablename__ = "medical_records"
    __table_args__ = {"extend_existing": True} # 모델 재로딩 방지

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    patient_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("patients.id"), nullable=False)
    chart_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    symptoms: Mapped[str] = mapped_column(Text, nullable=False)

    # 문자열로 관계를 정의하여 로딩 순서 충돌 방지
    patient: Mapped["Patient"] = relationship("Patient", back_populates="medical_records")
    xray_images: Mapped[list["XrayImage"]] = relationship("XrayImage", back_populates="medical_record")
    ai_analysis_results: Mapped[list["AiAnalysisResult"]] = relationship("AiAnalysisResult", back_populates="medical_record")