from datetime import datetime
from typing import Optional, List, Any
from sqlalchemy import String, Integer, DateTime, Enum, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.enums import EligibilityStatusEnum


class SchemeEligibilityRecord(Base):
    """
    Persisted evaluation & officer override log for a family's eligibility for a specific welfare scheme.
    """
    __tablename__ = "scheme_eligibility_record"

    record_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    family_id: Mapped[str] = mapped_column(String(20), ForeignKey("family.family_id"), nullable=False, index=True)
    scheme_id: Mapped[str] = mapped_column(String(36), ForeignKey("scheme.scheme_id"), nullable=False, index=True)

    status: Mapped[EligibilityStatusEnum] = mapped_column(
        Enum(EligibilityStatusEnum, native_enum=False, length=50),
        nullable=False,
        index=True
    )
    
    missing_documents: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    evaluation_details: Mapped[Optional[List[dict]]] = mapped_column(JSON, nullable=True) # list of {rule: str, passed: bool, detail: str}
    
    evaluated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Officer Review Fields
    reviewed_by_user_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("user_account.user_id"), nullable=True)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    officer_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    family: Mapped["Family"] = relationship("Family", back_populates="eligibility_records")
    scheme: Mapped["Scheme"] = relationship("Scheme")
