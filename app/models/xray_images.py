from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.databases import Base
from app.core.db.models import TimestampMixin
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.users import User

class XrayImage(Base, TimestampMixin):
    __tablename__ = "xray_images"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    record_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("medical_records.id"),
        nullable=False,
    )
    uploader_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=False,
    )
    image_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    shooting_datetime: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    medical_record: Mapped["MedicalRecord"] = relationship(
        "MedicalRecord",
        back_populates="xray_images",
    )
    uploader: Mapped["User"] = relationship(
        "User",
        back_populates="uploaded_xray_images",
    )
