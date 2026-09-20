from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class CategoryResponseSchema(BaseModel):
    category_id: int
    name: str
    icon_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class SchemeResponseSchema(BaseModel):
    scheme_id: str
    code: str
    name: str
    short_description: str
    benefit_summary: str
    level: str
    department: str
    category_id: int
    category_name: Optional[str] = None
    benefit_type: str
    eligibility_unit: str
    target_groups: Optional[List[str]] = []
    official_url: str
    require_officer_confirmation_before_apply: bool
    source_system: str
    last_synced_at: str

    model_config = ConfigDict(from_attributes=True)
