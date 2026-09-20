from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.enums import DocumentTypeEnum, DocumentStatusEnum


class Document(Base):
    """
    Household Document Vault record (e.g. Income Certificate, Caste Certificate, Land Record).
    """
    __tablename__ = "document"

    document_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    family_id: Mapped[str] = mapped_column(String(20), ForeignKey("family.family_id"), nullable=False, index=True)
    person_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("person.person_id"), nullable=True, index=True)
    
    document_type: Mapped[DocumentTypeEnum] = mapped_column(
        Enum(DocumentTypeEnum, native_enum=False, length=50), nullable=False, index=True
    )
    document_number: Mapped[str] = mapped_column(String(100), nullable=False)
    issuing_authority: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    
    issue_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    expiry_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    status: Mapped[DocumentStatusEnum] = mapped_column(
        Enum(DocumentStatusEnum, native_enum=False, length=50),
        default=DocumentStatusEnum.PENDING,
        nullable=False,
        index=True
    )
    
    verified_by_user_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("user_account.user_id"), nullable=True)
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    family: Mapped["Family"] = relationship("Family", back_populates="documents")
    person: Mapped[Optional["Person"]] = relationship("Person")
