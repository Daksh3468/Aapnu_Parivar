from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ApplicationStatusEnum


class ApplicationCreateSchema(BaseModel):
    scheme_id: str
    applicant_person_id: Optional[str] = None


class ApplicationHistorySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status: ApplicationStatusEnum
    source_system: str
    message: Optional[str] = None
    occurred_at: datetime


class ApplicationResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    application_id: str
    family_id: str
    scheme_id: str
    scheme_code: str
    scheme_name: str
    external_reference: str
    source_system: str
    official_url: str
    status: ApplicationStatusEnum
    last_synced_at: Optional[datetime] = None
    submitted_at: datetime
    officer_feedback: Optional[str] = None
    history: list[ApplicationHistorySchema]
