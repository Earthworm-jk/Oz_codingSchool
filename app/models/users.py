from __future__ import annotations
import enum
import uuid
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy import BigInteger, String, Enum, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db.databases import Base
from app.core.db.models import TimestampMixin, UUIDMixin
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.xray_images import XrayImage

# Enum 정의는 클래스 위에 위치해야 합니다.
class UserRole(str, enum.Enum):
    PENDING = "pending"
    STAFF = "staff"
    ADMIN = "admin"

class NationalityType(str, enum.Enum):
    KOREAN = "korean"
    FOREIGNER = "foreigner"

class User(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "users"
    __table_args__ = {"extend_existing": True}

    # PK 설정: id를 메인 PK로 사용
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    
    uuid: Mapped[str] = mapped_column(CHAR(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    
    employee_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    
    nationality: Mapped[NationalityType] = mapped_column(Enum(NationalityType), nullable=False)
    first_name: Mapped[str] = mapped_column(String(20), nullable=False)
    last_name: Mapped[str | None] = mapped_column(String(20), nullable=True)
    middle_name: Mapped[str | None] = mapped_column(String(20), nullable=True)
    
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    phone_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    gender: Mapped[str] = mapped_column(String(10), nullable=False)
    department: Mapped[str] = mapped_column(String(50), nullable=False)
    
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.PENDING, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1")

    # 관계 설정 (XrayImage 모델이 정의된 후 동작)
    uploaded_xray_images: Mapped[list["XrayImage"]] = relationship(
        "XrayImage",
        back_populates="uploader"
    )