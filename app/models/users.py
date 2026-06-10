from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy import BigInteger, Boolean, String, Column, Integer, Boolean, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.databases import Base
from app.core.db.models import TimestampMixin

if TYPE_CHECKING:
    from app.models.xray_images import XrayImage

class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(20), nullable=False)
    first_name: Mapped[str] = mapped_column(String(20), nullable=False)
    last_name: Mapped[str | None] = mapped_column(String(20), nullable=True)
    middle_name: Mapped[str | None] = mapped_column(String(20), nullable=True)
    employee_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    phone_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)

    # Enum 구조 유지
    nationality = Column(Enum("korean", "foreigner", name="nationality"), nullable=False)
    gender = Column(Enum("male", "female", name="gender"), nullable=False)
    department = Column(Enum("developer", "medical team", "researcher", name="department"), nullable=False)
    role: Mapped[str] = mapped_column(
    Enum("pending", "staff", "admin", name="role"),
    nullable=False,
    default="pending",
    server_default="pending" )
    
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="1")

    uploaded_xray_images: Mapped[list["XrayImage"]] = relationship(
        "XrayImage",
        back_populates="uploader",
    )