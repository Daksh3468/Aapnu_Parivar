from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship

from app.core.db import Base
from app.models.enums import LifeEventTypeEnum, SplitStatusEnum


class LifeEventRecord(Base):
    __tablename__ = "life_event_record"

    event_id = Column(Integer, primary_key=True, autoincrement=True)
    family_id = Column(String(36), ForeignKey("family.family_id"), nullable=False, index=True)
    person_id = Column(String(36), ForeignKey("person.person_id"), nullable=True, index=True)
    event_type = Column(Enum(LifeEventTypeEnum), nullable=False)
    event_date = Column(String(20), nullable=False)
    description = Column(Text, nullable=True)
    details_json = Column(JSON, nullable=True)
    registered_by_user_id = Column(String(36), ForeignKey("user_account.user_id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    family = relationship("Family", foreign_keys=[family_id])
    person = relationship("Person", foreign_keys=[person_id])
    registered_by = relationship("UserAccount", foreign_keys=[registered_by_user_id])


class FamilySplitRecord(Base):
    __tablename__ = "family_split_record"

    split_id = Column(Integer, primary_key=True, autoincrement=True)
    source_family_id = Column(String(36), ForeignKey("family.family_id"), nullable=False, index=True)
    new_family_id = Column(String(36), ForeignKey("family.family_id"), nullable=True, index=True)
    requested_by_user_id = Column(String(36), ForeignKey("user_account.user_id"), nullable=False)
    moved_person_ids_json = Column(JSON, nullable=False)
    new_head_person_id = Column(String(36), nullable=False)
    replacement_source_head_person_id = Column(String(36), nullable=True)
    split_reason = Column(Text, nullable=True)
    anomaly_score = Column(Float, default=0.0, nullable=False)
    anomaly_reasons_json = Column(JSON, nullable=True)
    status = Column(Enum(SplitStatusEnum), default=SplitStatusEnum.AUTOMATICALLY_APPROVED, nullable=False)
    reviewed_by_user_id = Column(String(36), ForeignKey("user_account.user_id"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    officer_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    source_family = relationship("Family", foreign_keys=[source_family_id])
    new_family = relationship("Family", foreign_keys=[new_family_id])
    requested_by = relationship("UserAccount", foreign_keys=[requested_by_user_id])
    reviewed_by = relationship("UserAccount", foreign_keys=[reviewed_by_user_id])
