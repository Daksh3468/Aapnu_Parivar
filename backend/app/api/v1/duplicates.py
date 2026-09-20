from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.auth_deps import get_current_user
from app.core.db import get_db
from app.core.jurisdiction import apply_family_jurisdiction_filter, build_officer_jurisdiction_scope
from app.models.duplicate import DuplicateFlag
from app.models.enums import UserRoleEnum
from app.models.family import Family
from app.models.membership import FamilyMembership
from app.models.user import UserAccount
from app.services.audit_service import write_audit

router = APIRouter()


class DuplicateResolutionSchema(BaseModel):
    status: Literal["NOT_DUPLICATE", "CONFIRMED_DUPLICATE", "NEEDS_INFO"]


def _require_officer(user: UserAccount) -> None:
    if user.role in {UserRoleEnum.CITIZEN_HEAD, UserRoleEnum.CITIZEN_MEMBER}:
        raise HTTPException(status_code=403, detail="Citizens cannot access duplicate review.")


def _family_in_scope(db: Session, person_id: str, user: UserAccount) -> Family | None:
    membership = db.query(FamilyMembership).filter(FamilyMembership.person_id == person_id, FamilyMembership.end_date.is_(None)).first()
    if not membership:
        return None
    return apply_family_jurisdiction_filter(db.query(Family).filter(Family.family_id == membership.family_id), build_officer_jurisdiction_scope(user)).first()


@router.get("/officer/duplicates", response_model=list[dict])
def list_duplicate_flags(db: Session = Depends(get_db), current_user: UserAccount = Depends(get_current_user)):
    _require_officer(current_user)
    flags = db.query(DuplicateFlag).filter(DuplicateFlag.status.in_(["OPEN", "NEEDS_INFO"])).order_by(DuplicateFlag.score.desc()).all()
    results = []
    for flag in flags:
        family = _family_in_scope(db, flag.person_a_id, current_user)
        if family:
            results.append({"flag_id": flag.flag_id, "family_id": family.family_id, "score": flag.score, "severity": flag.severity, "reasons": flag.reasons or {}, "status": flag.status, "created_at": flag.created_at})
    return results


@router.post("/officer/duplicates/{flag_id}/resolve", response_model=dict)
def resolve_duplicate_flag(flag_id: str, payload: DuplicateResolutionSchema, db: Session = Depends(get_db), current_user: UserAccount = Depends(get_current_user)):
    _require_officer(current_user)
    flag = db.query(DuplicateFlag).filter(DuplicateFlag.flag_id == flag_id).first()
    if not flag:
        raise HTTPException(status_code=404, detail="Duplicate flag not found.")
    family = _family_in_scope(db, flag.person_a_id, current_user)
    if not family:
        raise HTTPException(status_code=403, detail="Duplicate flag is outside officer jurisdiction scope.")
    flag.status = payload.status
    flag.resolved_by_user_id = current_user.user_id
    flag.resolved_at = datetime.utcnow()
    db.commit()
    write_audit(db, current_user.user_id, current_user.role.value, "RESOLVE_DUPLICATE", "duplicate_flag", flag.flag_id, family.family_id, purpose="Duplicate identity review", details={"status": payload.status})
    return {"flag_id": flag.flag_id, "status": flag.status}
