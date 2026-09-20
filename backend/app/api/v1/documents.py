from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.auth_deps import get_current_user
from app.core.jurisdiction import JurisdictionScope, build_officer_jurisdiction_scope, apply_family_jurisdiction_filter
from app.models.user import UserAccount
from app.models.family import Family
from app.models.document import Document
from app.models.enums import DocumentStatusEnum, UserRoleEnum
from app.schemas.document import DocumentCreateSchema, DocumentVerifySchema, DocumentResponseSchema
from app.services.audit_service import write_audit

router = APIRouter(tags=["Document Vault"])


@router.get("/families/{family_id}/documents", response_model=List[DocumentResponseSchema])
def list_family_documents(
    family_id: str,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Retrieves all documents associated with a household.
    """
    family = db.query(Family).filter(Family.family_id == family_id).first()
    if not family:
        raise HTTPException(status_code=404, detail="Family not found")

    scope = build_officer_jurisdiction_scope(current_user)
    if current_user.role not in [UserRoleEnum.CITIZEN_HEAD, UserRoleEnum.CITIZEN_MEMBER]:
        scoped_q = apply_family_jurisdiction_filter(db.query(Family).filter(Family.family_id == family_id), scope)
        if not scoped_q.first():
            raise HTTPException(status_code=403, detail="Family is out of officer jurisdiction scope")

    docs = db.query(Document).filter(Document.family_id == family_id).all()
    return [DocumentResponseSchema.model_validate(d) for d in docs]


@router.post("/families/{family_id}/documents", response_model=DocumentResponseSchema, status_code=status.HTTP_201_CREATED)
def create_family_document(
    family_id: str,
    payload: DocumentCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Registers a new document (Income Certificate, Caste Certificate, Land Record, etc.) in the vault.
    """
    family = db.query(Family).filter(Family.family_id == family_id).first()
    if not family:
        raise HTTPException(status_code=404, detail="Family not found")

    scope = build_officer_jurisdiction_scope(current_user)
    if current_user.role not in [UserRoleEnum.CITIZEN_HEAD, UserRoleEnum.CITIZEN_MEMBER]:
        scoped_q = apply_family_jurisdiction_filter(db.query(Family).filter(Family.family_id == family_id), scope)
        if not scoped_q.first():
            raise HTTPException(status_code=403, detail="Family is out of officer jurisdiction scope")

    initial_status = DocumentStatusEnum.VERIFIED if payload.document_number.startswith("GJ-VERIFIED") else DocumentStatusEnum.PENDING

    doc = Document(
        family_id=family_id,
        person_id=payload.person_id,
        document_type=payload.document_type,
        document_number=payload.document_number,
        issuing_authority=payload.issuing_authority or "Tahsildar / Revenue Department, Gujarat",
        issue_date=payload.issue_date,
        expiry_date=payload.expiry_date,
        file_path=payload.file_path or f"/vault/{family_id}/{payload.document_type.value}.pdf",
        status=initial_status,
    )
    if initial_status == DocumentStatusEnum.VERIFIED:
        doc.verified_at = datetime.utcnow()
        doc.verified_by_user_id = current_user.user_id

    db.add(doc)
    db.commit()
    db.refresh(doc)

    write_audit(
        db,
        actor_user_id=str(current_user.user_id),
        actor_role=current_user.role.value,
        action="DOCUMENT_UPLOAD",
        entity_type="document",
        entity_id=str(doc.document_id),
        family_id=family_id,
        details={"document_type": payload.document_type.value},
    )

    return DocumentResponseSchema.model_validate(doc)


@router.post("/documents/{document_id}/verify", response_model=DocumentResponseSchema)
def verify_or_reject_document(
    document_id: int,
    payload: DocumentVerifySchema,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Department Officer endpoint to verify or reject a document.
    """
    if current_user.role in [UserRoleEnum.CITIZEN_HEAD, UserRoleEnum.CITIZEN_MEMBER]:
        raise HTTPException(status_code=403, detail="Citizens cannot verify document vault records")

    doc = db.query(Document).filter(Document.document_id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    scope = build_officer_jurisdiction_scope(current_user)
    scoped_q = apply_family_jurisdiction_filter(db.query(Family).filter(Family.family_id == doc.family_id), scope)
    if not scoped_q.first():
        raise HTTPException(status_code=403, detail="Document's household is out of officer jurisdiction scope")

    doc.status = payload.status
    doc.verified_by_user_id = current_user.user_id
    doc.verified_at = datetime.utcnow()
    doc.rejection_reason = payload.rejection_reason if payload.status == DocumentStatusEnum.REJECTED else None

    db.commit()
    db.refresh(doc)

    write_audit(
        db,
        actor_user_id=str(current_user.user_id),
        actor_role=current_user.role.value,
        action="DOCUMENT_VERIFIED" if payload.status == DocumentStatusEnum.VERIFIED else "DOCUMENT_REJECTED",
        entity_type="document",
        entity_id=str(doc.document_id),
        family_id=doc.family_id,
        details={"status": payload.status.value, "reason": payload.rejection_reason},
    )

    return DocumentResponseSchema.model_validate(doc)


@router.get("/officer/documents-queue", response_model=List[DocumentResponseSchema])
def get_officer_documents_queue(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Retrieves all pending document vault verification requests within officer's jurisdiction.
    """
    if current_user.role in [UserRoleEnum.CITIZEN_HEAD, UserRoleEnum.CITIZEN_MEMBER]:
        raise HTTPException(status_code=403, detail="Citizens cannot access officer document review queues")

    scope = build_officer_jurisdiction_scope(current_user)
    scoped_families = apply_family_jurisdiction_filter(db.query(Family), scope).all()
    family_ids = [f.family_id for f in scoped_families]

    docs = db.query(Document).filter(
        Document.family_id.in_(family_ids),
        Document.status == DocumentStatusEnum.PENDING
    ).all()

    return [DocumentResponseSchema.model_validate(d) for d in docs]


