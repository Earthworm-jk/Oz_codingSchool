from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


Gender = Literal["male", "female"]


class PatientCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=30)
    age: int = Field(ge=0, le=150)
    gender: Gender
    phone_number: str = Field(min_length=10, max_length=11)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()
        if not (2 <= len(value) <= 30):
            raise ValueError("환자 이름은 최소 2글자, 최대 30글자여야 합니다.")
        return value

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, value: str) -> str:
        if not value.isdigit():
            raise ValueError("전화번호는 숫자만 입력해야 합니다.")
        return value


class PatientUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=30)
    age: int | None = Field(default=None, ge=0, le=150)
    gender: Gender | None = None
    phone_number: str | None = Field(default=None, min_length=10, max_length=11)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.strip()
        if not (2 <= len(value) <= 30):
            raise ValueError("환자 이름은 최소 2글자, 최대 30글자여야 합니다.")
        return value

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, value: str | None) -> str | None:
        if value is not None and not value.isdigit():
            raise ValueError("전화번호는 숫자만 입력해야 합니다.")
        return value


class PatientResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    age: int
    gender: str
    phone_number: str
    created_at: datetime
    updated_at: datetime | None = None


class MedicalRecordUpdateRequest(BaseModel):
    chart_number: str | None = Field(default=None, min_length=1, max_length=50)
    symptoms: str | None = Field(default=None, min_length=1)

    @field_validator("chart_number")
    @classmethod
    def validate_chart_number(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("차트번호는 필수 입력 항목입니다.")
        return value

    @field_validator("symptoms")
    @classmethod
    def validate_symptoms(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("증상은 필수 입력 항목입니다.")
        return value


class MedicalRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: int
    chart_number: str
    symptoms: str
    xray_image_url: str | None = None
    shooting_datetime: datetime | None = None
    created_at: datetime
    updated_at: datetime | None = None


class AiAnalysisResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    record_id: int
    is_pneumonia: bool | None = None
    confidence: Decimal | None = None
    heatmap_url: str | None = None
    ai_model: str | None = None
    xray_image_url: str | None = None
    chart_number: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

