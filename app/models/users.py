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

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=True)
    middle_name = Column(String, nullable=True)
    employee_number = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    
    # Enum 구조 유지
    nationality = Column(Enum("korean", "foreigner", name="nationality"), nullable=False)
    gender = Column(Enum("male", "female", name="gender"), nullable=False)
    department = Column(Enum("developer", "medical team", "researcher", name="department"), nullable=False)
    role = Column(Enum("pending", "staff", "admin", name="role"), default="pending", nullable=False)
    
    is_active = Column(Boolean, default=True)

    uploaded_xray_images: Mapped[list["XrayImage"]] = relationship(
        "XrayImage",
        back_populates="uploader",
    )