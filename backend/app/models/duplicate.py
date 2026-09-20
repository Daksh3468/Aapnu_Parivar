import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Enum, DateTime, JSON, ForeignKey
from app.core.db import Base


class DuplicateFlag(Base):
    __tablename__ = "duplicate_flag"

    flag_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    person_a_id = Column(String(36), ForeignKey("person.person_id"), nullable=False, index=True)
    person_b_id = Column(String(36), ForeignKey("person.person_id"), nullable=False, index=True)

    score = Column(Float, nullable=False)
    severity = Column(String(20), nullable=False)  # HIGH, MEDIUM
    reasons = Column(JSON, nullable=True)

    status = Column(String(30), nullable=False, default="OPEN", index=True)  # OPEN, NOT_DUPLICATE, CONFIRMED_DUPLICATE, NEEDS_INFO
    resolved_by_user_id = Column(String(36), nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
