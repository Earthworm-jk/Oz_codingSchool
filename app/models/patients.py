from __future__ import annotations

from sqlalchemy import BigInteger, Enum, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.databases import Base
from app.core.db.models import TimestampMixin


class Patient(Base, TimestampMixin):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    age: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    gender: Mapped[str] = mapped_column(
        Enum("male", "female", name="gender"),
        nullable=False,
    )
    phone: Mapped[str] = mapped_column(String(11), nullable=False)

    medical_records: Mapped[list["MedicalRecord"]] = relationship(
        "MedicalRecord",
        back_populates="patient",
    )
