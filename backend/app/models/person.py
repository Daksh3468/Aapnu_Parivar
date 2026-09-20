import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, Date, DateTime, Boolean, Enum, Integer
from sqlalchemy.orm import relationship
from app.core.db import Base
from app.models.enums import (
    GenderEnum,
    MaritalStatusEnum,
    VerificationStatusEnum,
    SocialCategoryEnum,
    EducationLevelEnum,
    OccupationTypeEnum,
)


class Person(Base):
    __tablename__ = "person"

    person_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    full_name = Column(String(200), nullable=False)
    dob = Column(Date, nullable=False)
    gender = Column(Enum(GenderEnum), nullable=False)
    marital_status = Column(Enum(MaritalStatusEnum), nullable=False, default=MaritalStatusEnum.UNMARRIED)
    mobile = Column(String(15), nullable=True, index=True)
    email = Column(String(100), nullable=True)

    aadhaar_last4 = Column(String(4), nullable=True)
    aadhaar_hash = Column(String(64), unique=True, nullable=True, index=True)
    verification_status = Column(
        Enum(VerificationStatusEnum), nullable=False, default=VerificationStatusEnum.UNVERIFIED
    )
    verified_at = Column(DateTime, nullable=True)

    social_category = Column(Enum(SocialCategoryEnum), nullable=False, default=SocialCategoryEnum.GENERAL)
    education_level = Column(Enum(EducationLevelEnum), nullable=False, default=EducationLevelEnum.NONE)
    occupation_type = Column(Enum(OccupationTypeEnum), nullable=False, default=OccupationTypeEnum.OTHER)

    disability_type = Column(String(100), nullable=True)
    disability_percent = Column(Integer, nullable=True, default=0)

    has_bank_account = Column(Boolean, nullable=False, default=False)
    domicile_gujarat = Column(Boolean, nullable=False, default=True)

    is_deceased = Column(Boolean, nullable=False, default=False)
    date_of_death = Column(Date, nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    memberships = relationship("FamilyMembership", back_populates="person")
    user_account = relationship("UserAccount", back_populates="person", uselist=False)
