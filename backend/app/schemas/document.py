from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.enums import DocumentTypeEnum, DocumentStatusEnum


class DocumentCreateSchema(BaseModel):
    document_type: DocumentTypeEnum
    document_number: str
    issuing_authority: Optional[str] = None
    person_id: Optional[int] = None
    issue_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    file_path: Optional[str] = None


class DocumentVerifySchema(BaseModel):
    status: DocumentStatusEnum # VERIFIED or REJECTED
    rejection_reason: Optional[str] = None


class DocumentResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    document_id: int
    family_id: str
    person_id: Optional[int] = None
    document_type: DocumentTypeEnum
    document_number: str
    issuing_authority: Optional[str] = None
    issue_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    file_path: Optional[str] = None
    status: DocumentStatusEnum
    verified_by_user_id: Optional[str] = None
    verified_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    created_at: datetime
