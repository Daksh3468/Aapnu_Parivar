from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.auth_deps import get_current_user
from app.core.jurisdiction import JurisdictionScope, build_officer_jurisdiction_scope, apply_family_jurisdiction_filter
from app.models.user import UserAccount
from app.models.family import Family
from app.models.scheme import Scheme
from app.models.eligibility import SchemeEligibilityRecord
from app.models.enums import UserRoleEnum, EligibilityStatusEnum
from app.schemas.eligibility import SchemeEligibilityResponseSchema, OfficerEligibilityReviewSchema
from app.services.eligibility_service import EligibilityEngine
from app.services.audit_service import write_audit

router = APIRouter(tags=["Eligibility Engine & Officer Queue"])


@router.get("/families/{family_id}/eligibility", response_model=List[SchemeEligibilityResponseSchema])
def get_family_scheme_eligibility(
    family_id: str,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Evaluates or retrieves rule-based scheme eligibility for a given household across all active schemes.
    """
    family = db.query(Family).filter(Family.family_id == family_id).first()
    if not family:
        raise HTTPException(status_code=404, detail="Family not found")

    scope = build_officer_jurisdiction_scope(current_user)
    if current_user.role not in [UserRoleEnum.CITIZEN_HEAD, UserRoleEnum.CITIZEN_MEMBER]:
        scoped_q = apply_family_jurisdiction_filter(db.query(Family).filter(Family.family_id == family_id), scope)
        if not scoped_q.first():
            raise HTTPException(status_code=403, detail="Family is out of officer jurisdiction scope")

    results = EligibilityEngine.evaluate_all_schemes_for_family(db, family_id)
    return results


@router.post("/families/{family_id}/eligibility/{scheme_id}/review", response_model=SchemeEligibilityResponseSchema)
def review_family_eligibility(
    family_id: str,
    scheme_id: str,
    payload: OfficerEligibilityReviewSchema,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Department Officer endpoint to manually approve or reject eligibility for a household scheme application.
    """
    if current_user.role in [UserRoleEnum.CITIZEN_HEAD, UserRoleEnum.CITIZEN_MEMBER]:
        raise HTTPException(status_code=403, detail="Citizens cannot review eligibility records")

    scope = build_officer_jurisdiction_scope(current_user)
    scoped_q = apply_family_jurisdiction_filter(db.query(Family).filter(Family.family_id == family_id), scope)
    if not scoped_q.first():
        raise HTTPException(status_code=403, detail="Family is out of officer jurisdiction scope")

    rec = db.query(SchemeEligibilityRecord).filter(
        SchemeEligibilityRecord.family_id == family_id,
        SchemeEligibilityRecord.scheme_id == scheme_id
    ).first()

    if not rec:
        rec = SchemeEligibilityRecord(
            family_id=family_id,
            scheme_id=scheme_id,
            status=payload.status,
            reviewed_by_user_id=current_user.user_id,
            reviewed_at=datetime.utcnow(),
            officer_notes=payload.officer_notes,
        )
        db.add(rec)
    else:
        rec.status = payload.status
        rec.reviewed_by_user_id = current_user.user_id
        rec.reviewed_at = datetime.utcnow()
        rec.officer_notes = payload.officer_notes

    db.commit()

    # Re-evaluate family scheme eligibility list to return updated item
    results = EligibilityEngine.evaluate_all_schemes_for_family(db, family_id)
    target = next((r for r in results if r.scheme_id == scheme_id), None)
    if not target:
        raise HTTPException(status_code=404, detail="Scheme not found")

    write_audit(
        db,
        actor_user_id=str(current_user.user_id),
        actor_role=current_user.role.value,
        action="ELIGIBILITY_OFFICER_REVIEW",
        entity_type="scheme_eligibility_record",
        entity_id=f"{family_id}:{scheme_id}",
        family_id=family_id,
        details={"status": payload.status.value, "notes": payload.officer_notes},
    )

    return target


@router.get("/officer/eligibility-queue", response_model=List[dict])
def get_officer_eligibility_queue(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Retrieves household applications or eligibility flags requiring departmental review within officer's jurisdiction.
    """
    if current_user.role in [UserRoleEnum.CITIZEN_HEAD, UserRoleEnum.CITIZEN_MEMBER]:
        raise HTTPException(status_code=403, detail="Citizens cannot access officer review queues")

    scope = build_officer_jurisdiction_scope(current_user)
    query = apply_family_jurisdiction_filter(db.query(Family), scope)
    families = query.all()

    queue_items = []
    for fam in families:
        records = db.query(SchemeEligibilityRecord).filter(
            SchemeEligibilityRecord.family_id == fam.family_id,
            SchemeEligibilityRecord.status.in_([
                EligibilityStatusEnum.DOCS_NEEDED,
                EligibilityStatusEnum.OFFICER_APPROVED,
                EligibilityStatusEnum.OFFICER_REJECTED
            ])
        ).all()

        head_member = next((m for m in fam.memberships if m.role_in_family == "HEAD" and m.end_date is None), None)
        head_name = f"{head_member.person.first_name} {head_member.person.last_name}" if head_member and head_member.person else "Household Head"

        for r in records:
            queue_items.append({
                "record_id": r.record_id,
                "family_id": fam.family_id,
                "head_name": head_name,
                "district_id": fam.address.district_id if fam.address else None,
                "scheme_id": r.scheme_id,
                "scheme_name": r.scheme.name if r.scheme else f"Scheme #{r.scheme_id}",
                "status": r.status.value,
                "missing_documents": r.missing_documents or [],
                "evaluated_at": r.evaluated_at.isoformat() if r.evaluated_at else None,
                "officer_notes": r.officer_notes,
            })

    return queue_items

