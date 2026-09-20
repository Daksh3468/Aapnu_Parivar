import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Enum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.db import Base
from app.models.enums import UserRoleEnum, UserAccountStatusEnum, JurisdictionScopeEnum


class UserAccount(Base):
    __tablename__ = "user_account"

    user_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    person_id = Column(String(36), ForeignKey("person.person_id"), nullable=True, unique=True)
    role = Column(Enum(UserRoleEnum), nullable=False, default=UserRoleEnum.CITIZEN_MEMBER, index=True)

    login_id = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    status = Column(Enum(UserAccountStatusEnum), nullable=False, default=UserAccountStatusEnum.ACTIVE)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)

    person = relationship("Person", back_populates="user_account")
    jurisdictions = relationship("OfficerJurisdiction", back_populates="user_account")
    otp_challenges = relationship("OTPChallenge", back_populates="user_account")


class OfficerJurisdiction(Base):
    __tablename__ = "officer_jurisdiction"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("user_account.user_id"), nullable=False, index=True)
    scope_type = Column(Enum(JurisdictionScopeEnum), nullable=False, default=JurisdictionScopeEnum.STATE)
    district_code = Column(Integer, ForeignKey("district.district_code"), nullable=True, index=True)
    pincode = Column(String(6), nullable=True, index=True)

    user_account = relationship("UserAccount", back_populates="jurisdictions")


class OTPChallenge(Base):
    __tablename__ = "otp_challenge"

    challenge_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("user_account.user_id"), nullable=True, index=True)
    target_mobile = Column(String(15), nullable=False, index=True)
    purpose = Column(String(50), nullable=False)  # LOGIN, RESET, CLAIM, AADHAAR_KYC
    code_hash = Column(String(255), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    attempts = Column(Integer, nullable=False, default=0)
    used_at = Column(DateTime, nullable=True)

    user_account = relationship("UserAccount", back_populates="otp_challenges")
