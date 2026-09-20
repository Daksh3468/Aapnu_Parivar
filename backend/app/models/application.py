import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Index, JSON, String, Text, text
from sqlalchemy.orm import relationship

from app.core.db import Base
from app.models.enums import ApplicationStatusEnum


class SchemeApplication(Base):
    """A family application linked to an external (mock) government portal."""

    __tablename__ = "scheme_application"

    application_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    family_id = Column(String(20), ForeignKey("family.family_id"), nullable=False, index=True)
    scheme_id = Column(String(36), ForeignKey("scheme.scheme_id"), nullable=False, index=True)
    applicant_person_id = Column(String(36), ForeignKey("person.person_id"), nullable=True, index=True)
    applicant_token = Column(String(64), nullable=False, index=True)
    source_system = Column(String(100), nullable=False)
    external_reference = Column(String(80), nullable=False, unique=True, index=True)
    official_url = Column(String(255), nullable=False)
    status = Column(Enum(ApplicationStatusEnum), nullable=False, default=ApplicationStatusEnum.SUBMITTED, index=True)
    last_synced_at = Column(DateTime, nullable=True)
    officer_feedback = Column(Text, nullable=True)
    submitted_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    payload_snapshot = Column(JSON, nullable=False, default=dict)

    family = relationship("Family", back_populates="applications")
    scheme = relationship("Scheme")
    history = relationship("ApplicationStatusHistory", back_populates="application", cascade="all, delete-orphan")

    __table_args__ = (
        Index(
            "ux_active_application_per_family_scheme",
            "family_id",
            "scheme_id",
            unique=True,
            sqlite_where=text("status IN ('SUBMITTED', 'UNDER_REVIEW', 'APPROVED')"),
            postgresql_where=text("status IN ('SUBMITTED', 'UNDER_REVIEW', 'APPROVED')"),
        ),
    )


class ApplicationStatusHistory(Base):
    __tablename__ = "application_status_history"

    history_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    application_id = Column(String(36), ForeignKey("scheme_application.application_id"), nullable=False, index=True)
    status = Column(Enum(ApplicationStatusEnum), nullable=False, index=True)
    source_system = Column(String(100), nullable=False)
    message = Column(Text, nullable=True)
    metadata_json = Column(JSON, nullable=True)
    occurred_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    application = relationship("SchemeApplication", back_populates="history")
