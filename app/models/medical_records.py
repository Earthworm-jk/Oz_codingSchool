from __future__ import annotations

from sqlalchemy import BigInteger, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.databases import Base
from app.core.db.models import TimestampMixin


class MedicalRecord(Base, TimestampMixin):
    __tablename__ = "medical_records"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    patient_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("patients.id"),
        nullable=False,
    )
    chart_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    symptoms: Mapped[str] = mapped_column(Text, nullable=False)

    patient: Mapped["Patient"] = relationship(
        "Patient",
        back_populates="medical_records",
    )
    xray_images: Mapped[list["XrayImage"]] = relationship(
        "XrayImage",
        back_populates="medical_record",
    )
    ai_analysis_results: Mapped[list["AiAnalysisResult"]] = relationship(
        "AiAnalysisResult",
        back_populates="medical_record",
    )
