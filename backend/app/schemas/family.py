from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict
from app.models.enums import (
    GenderEnum,
    MaritalStatusEnum,
    SocialCategoryEnum,
    EducationLevelEnum,
    OccupationTypeEnum,
    RationCardTypeEnum,
    IncomeBandEnum,
    HouseTypeEnum,
    RoleInFamilyEnum,
    RelationToHeadEnum,
)


class AddressCreateSchema(BaseModel):
    line1: str = Field(..., min_length=3, max_length=255, description="Street / House address")
    village_or_town: str = Field(..., min_length=2, max_length=100)
    taluka: str = Field(..., min_length=2, max_length=100)
    district_code: int = Field(..., ge=1, le=33, description="Gujarat district code (1 to 33)")
    pincode: str = Field(..., pattern=r"^\d{6}$", description="6-digit pincode")


class MemberCreateSchema(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=200)
    dob: date = Field(...)
    gender: GenderEnum
    marital_status: MaritalStatusEnum = MaritalStatusEnum.UNMARRIED
    mobile: Optional[str] = Field(None, pattern=r"^\d{10}$")
    relation_to_head: RelationToHeadEnum
    social_category: SocialCategoryEnum = SocialCategoryEnum.GENERAL
    education_level: EducationLevelEnum = EducationLevelEnum.NONE
    occupation_type: OccupationTypeEnum = OccupationTypeEnum.OTHER
    has_bank_account: bool = False
    is_head: bool = False

    @field_validator("dob")
    @classmethod
    def validate_dob(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("Date of birth cannot be in the future")
        return v


class FamilyRegisterPayload(BaseModel):
    address: AddressCreateSchema
    head: MemberCreateSchema
    members: List[MemberCreateSchema] = []

    password: Optional[str] = Field(None, min_length=6, description="First time login password set during family registration")
    ration_card_number: Optional[str] = None
    ration_card_type: RationCardTypeEnum = RationCardTypeEnum.NONE
    annual_income_amount: Optional[float] = Field(None, ge=0)
    income_band: IncomeBandEnum = IncomeBandEnum.LT_1L
    land_holding_acres: float = Field(0.0, ge=0.0)
    house_type: HouseTypeEnum = HouseTypeEnum.NONE
    house_owned: bool = True
    has_lpg_connection: bool = False
    primary_occupation: OccupationTypeEnum = OccupationTypeEnum.OTHER
    consent_given: bool = Field(True, description="Mandatory citizen consent flag")

    @field_validator("head")
    @classmethod
    def validate_head_age(cls, v: MemberCreateSchema) -> MemberCreateSchema:
        # Calculate age of head
        today = date.today()
        age = today.year - v.dob.year - ((today.month, today.day) < (v.dob.month, v.dob.day))
        if age < 18:
            raise ValueError("Head of family must be at least 18 years old")
        return v


# Response Schemas
class MemberResponseSchema(BaseModel):
    person_id: str
    full_name: str
    dob: date
    gender: str
    marital_status: str
    mobile_masked: Optional[str] = None
    relation_to_head: str
    role_in_family: str
    verification_status: str
    aadhaar_last4: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class AddressResponseSchema(BaseModel):
    address_id: str
    line1: str
    village_or_town: str
    taluka: str
    district_code: int
    district_name: Optional[str] = None
    pincode: str

    model_config = ConfigDict(from_attributes=True)


class FamilyResponseSchema(BaseModel):
    family_id: str
    status: str
    registered_by: str
    created_at: str
    address: AddressResponseSchema
    head_name: str
    ration_card_type: str
    income_band: str
    member_count: int
    members: List[MemberResponseSchema] = []

    model_config = ConfigDict(from_attributes=True)
