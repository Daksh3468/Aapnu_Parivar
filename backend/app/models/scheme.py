import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Enum, DateTime, JSON, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.db import Base
import enum


class SchemeLevelEnum(str, enum.Enum):
    CENTRAL = "CENTRAL"
    STATE = "STATE"  # Gujarat Government


class BenefitTypeEnum(str, enum.Enum):
    CASH = "CASH"
    IN_KIND = "IN_KIND"
    INSURANCE = "INSURANCE"
    SUBSIDY = "SUBSIDY"
    LOAN = "LOAN"
    SERVICE = "SERVICE"


class EligibilityUnitEnum(str, enum.Enum):
    FAMILY = "FAMILY"
    INDIVIDUAL = "INDIVIDUAL"


class SchemeCategory(Base):
    __tablename__ = "scheme_category"

    category_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    icon_name = Column(String(50), nullable=True)

    schemes = relationship("Scheme", back_populates="category")


class Scheme(Base):
    __tablename__ = "scheme"

    scheme_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    short_description = Column(Text, nullable=False)
    benefit_summary = Column(Text, nullable=False)

    level = Column(Enum(SchemeLevelEnum), nullable=False, default=SchemeLevelEnum.STATE, index=True)
    department = Column(String(150), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("scheme_category.category_id"), nullable=False, index=True)

    benefit_type = Column(Enum(BenefitTypeEnum), nullable=False, default=BenefitTypeEnum.CASH)
    eligibility_unit = Column(Enum(EligibilityUnitEnum), nullable=False, default=EligibilityUnitEnum.FAMILY)
    target_groups = Column(JSON, nullable=True)  # e.g., ["FARMER", "WOMEN", "SC", "ST"]

    rules_key = Column(String(100), nullable=False)
    rule_version = Column(String(20), nullable=False, default="1.0")
    official_url = Column(String(255), nullable=False)
    require_officer_confirmation_before_apply = Column(Boolean, nullable=False, default=False)

    source_system = Column(String(100), nullable=False, default="DIGITAL_GUJARAT")
    last_synced_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    is_active = Column(Boolean, nullable=False, default=True)

    category = relationship("SchemeCategory", back_populates="schemes")
