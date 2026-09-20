import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON, Boolean, ForeignKey
from app.core.db import Base


class AuditLog(Base):
    __tablename__ = "audit_log"

    log_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    actor_user_id = Column(String(36), nullable=True, index=True)
    actor_role = Column(String(50), nullable=False)

    action = Column(String(50), nullable=False, index=True)  # CREATE, UPDATE, VIEW, APPROVE, LOGIN
    entity_type = Column(String(50), nullable=False, index=True)
    entity_id = Column(String(100), nullable=True)
    family_id = Column(String(20), nullable=True, index=True)

    purpose = Column(String(200), nullable=True)
    ip_address = Column(String(50), nullable=True)
    at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    details = Column(JSON, nullable=True)


class ConsentRecord(Base):
    __tablename__ = "consent_record"

    consent_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    person_id = Column(String(36), ForeignKey("person.person_id"), nullable=False, index=True)
    purpose = Column(String(100), nullable=False)  # REGISTRATION, ELIGIBILITY_CHECK, SCHEME_SYNC, NOTIFICATIONS
    mandatory = Column(Boolean, nullable=False, default=True)

    granted_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    revoked_at = Column(DateTime, nullable=True)
