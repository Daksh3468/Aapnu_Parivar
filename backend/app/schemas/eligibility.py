from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict
from app.models.enums import EligibilityStatusEnum
from app.models.scheme import BenefitTypeEnum, SchemeLevelEnum


class RuleEvaluationDetail(BaseModel):
    rule_name: str
    passed: bool
    description: str


class SchemeEligibilityResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    scheme_id: str
    scheme_code: str
    scheme_name: str
    category_name: str
    level: SchemeLevelEnum
    benefit_type: BenefitTypeEnum
    benefit_summary: str
    official_url: Optional[str] = None
    
    status: EligibilityStatusEnum
    missing_documents: List[str] = []
    evaluation_details: List[RuleEvaluationDetail] = []
    
    reviewed_by_user_id: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    officer_notes: Optional[str] = None


class OfficerEligibilityReviewSchema(BaseModel):
    status: EligibilityStatusEnum # OFFICER_APPROVED or OFFICER_REJECTED
    officer_notes: str
