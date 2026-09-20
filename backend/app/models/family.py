from datetime import datetime
from sqlalchemy import Column, String, Float, Numeric, Boolean, Enum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.db import Base
from app.models.enums import (
    FamilyStatusEnum,
    RationCardTypeEnum,
    IncomeBandEnum,
    HouseTypeEnum,
    OccupationTypeEnum,
    RegisteredByEnum,
)


class Family(Base):
    __tablename__ = "family"

    family_id = Column(String(20), primary_key=True, index=True)
    status = Column(Enum(FamilyStatusEnum), nullable=False, default=FamilyStatusEnum.SUBMITTED, index=True)
    address_id = Column(String(36), ForeignKey("address.address_id"), nullable=False, index=True)

    ration_card_number = Column(String(30), nullable=True)
    ration_card_type = Column(Enum(RationCardTypeEnum), nullable=False, default=RationCardTypeEnum.NONE)

    annual_income_amount = Column(Numeric(12, 2), nullable=True)
    income_band = Column(Enum(IncomeBandEnum), nullable=False, default=IncomeBandEnum.LT_1L)
    land_holding_acres = Column(Float, nullable=False, default=0.0)

    house_type = Column(Enum(HouseTypeEnum), nullable=False, default=HouseTypeEnum.NONE)
    house_owned = Column(Boolean, nullable=False, default=True)
    has_lpg_connection = Column(Boolean, nullable=False, default=False)
    primary_occupation = Column(Enum(OccupationTypeEnum), nullable=False, default=OccupationTypeEnum.OTHER)

    registered_by = Column(Enum(RegisteredByEnum), nullable=False, default=RegisteredByEnum.SELF)
    registered_by_user_id = Column(String(36), nullable=True)

    verified_by = Column(String(36), nullable=True)
    verified_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)

    address = relationship("Address", back_populates="families")
    memberships = relationship("FamilyMembership", back_populates="family")
    documents = relationship("Document", back_populates="family", cascade="all, delete-orphan")
    eligibility_records = relationship("SchemeEligibilityRecord", back_populates="family", cascade="all, delete-orphan")
    applications = relationship("SchemeApplication", back_populates="family", cascade="all, delete-orphan")
