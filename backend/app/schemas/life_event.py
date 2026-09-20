from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

from app.models.enums import LifeEventTypeEnum, SplitStatusEnum


class LifeEventCreateSchema(BaseModel):
    person_id: Optional[str] = Field(None, description="ID of specific person affected by event")
    event_type: LifeEventTypeEnum = Field(..., description="Type of event: BIRTH, DEATH, MARRIAGE_OUT, etc.")
    event_date: str = Field(..., description="YYYY-MM-DD date of event")
    description: Optional[str] = Field(None, description="Details or registration reference")
    details: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional event metadata")


class LifeEventResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    event_id: int
    family_id: str
    person_id: Optional[str] = None
    person_name: Optional[str] = None
    event_type: str
    event_date: str
    description: Optional[str] = None
    details_json: Optional[Dict[str, Any]] = None
    created_at: str


class SplitAddressSchema(BaseModel):
    line1: str = Field(..., description="Street or area address")
    village_or_town: str = Field(..., description="Village or town name")
    taluka: Optional[str] = Field(None, description="Taluka name")
    district_code: int = Field(..., description="Gujarat District Code (1-33)")
    pincode: str = Field(..., description="6-digit Pincode")


class FamilySplitRequestSchema(BaseModel):
    moved_person_ids: List[str] = Field(..., min_length=1, description="List of person IDs moving to new family")
    new_head_person_id: str = Field(..., description="Person ID designated as Head of New Family")
    replacement_source_head_person_id: Optional[str] = Field(None, description="Replacement Head for source family if original head moves out")
    split_reason: Optional[str] = Field(None, description="Stated reason for splitting household")
    new_address: Optional[SplitAddressSchema] = Field(None, description="Address for the new household")


class FamilySplitResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    split_id: int
    source_family_id: str
    new_family_id: Optional[str] = None
    requested_by_user_id: str
    moved_person_ids: List[str]
    new_head_person_id: str
    split_reason: Optional[str] = None
    anomaly_score: float
    anomaly_reasons: List[str] = []
    status: str
    officer_notes: Optional[str] = None
    created_at: str


class OfficerSplitReviewSchema(BaseModel):
    status: SplitStatusEnum = Field(..., description="OFFICER_APPROVED or OFFICER_REJECTED")
    officer_notes: Optional[str] = Field(None, description="Notes or justification for decision")
