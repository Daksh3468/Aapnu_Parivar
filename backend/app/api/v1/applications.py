from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth_deps import get_active_citizen_membership, get_current_user
from app.core.db import get_db
from app.core.jurisdiction import apply_family_jurisdiction_filter, build_officer_jurisdiction_scope
from app.models.application import SchemeApplication
from app.models.enums import UserRoleEnum
from app.models.family import Family
from app.models.scheme import Scheme
from app.models.user import UserAccount
from app.schemas.application import ApplicationCreateSchema, ApplicationHistorySchema, ApplicationResponseSchema
from app.services.application_service import create_application, refresh_application
from app.services.audit_service import write_audit

router = APIRouter()
CITIZEN_ROLES = {UserRoleEnum.CITIZEN_HEAD, UserRoleEnum.CITIZEN_MEMBER}


def _authorize_family(db: Session, family_id: str, user: UserAccount, *, applying: bool = False) -> Family:
    family = db.query(Family).filter(Family.family_id == family_id).first()
    if not family:
        raise HTTPException(status_code=404, detail="Family not found.")
    if user.role in CITIZEN_ROLES:
        membership = get_active_citizen_membership(user, db)
        if not membership or membership.family_id != family_id:
            raise HTTPException(status_code=403, detail="You may access only your active household.")
        if applying and user.role != UserRoleEnum.CITIZEN_HEAD:
            raise HTTPException(status_code=403, detail="Only the household head can submit a scheme application.")
        return family
    scoped = apply_family_jurisdiction_filter(db.query(Family).filter(Family.family_id == family_id), build_officer_jurisdiction_scope(user)).first()
    if not scoped:
        raise HTTPException(status_code=403, detail="Family is out of officer jurisdiction scope.")
    if applying:
        raise HTTPException(status_code=403, detail="Officers cannot submit citizen applications.")
    return family


def _response(application: SchemeApplication) -> ApplicationResponseSchema:
    return ApplicationResponseSchema(
        application_id=application.application_id,
        family_id=application.family_id,
        scheme_id=application.scheme_id,
        scheme_code=application.scheme.code,
        scheme_name=application.scheme.name,
        external_reference=application.external_reference,
        source_system=application.source_system,
        official_url=application.official_url,
        status=application.status,
        last_synced_at=application.last_synced_at,
        submitted_at=application.submitted_at,
        officer_feedback=application.officer_feedback,
        history=[ApplicationHistorySchema.model_validate(item) for item in sorted(application.history, key=lambda row: row.occurred_at)],
    )


@router.post("/families/{family_id}/applications", response_model=ApplicationResponseSchema, status_code=201)
def submit_application(family_id: str, payload: ApplicationCreateSchema, db: Session = Depends(get_db), current_user: UserAccount = Depends(get_current_user)):
    family = _authorize_family(db, family_id, current_user, applying=True)
    scheme = db.query(Scheme).filter(Scheme.scheme_id == payload.scheme_id, Scheme.is_active.is_(True)).first()
    if not scheme:
        raise HTTPException(status_code=404, detail="Active scheme not found.")
    application = create_application(db, family, scheme, payload.applicant_person_id)
    write_audit(db, current_user.user_id, current_user.role.value, "SUBMIT_APPLICATION", "scheme_application", application.application_id, family_id, purpose="Citizen scheme application", details={"scheme_id": scheme.scheme_id, "external_reference": application.external_reference})
    return _response(application)


@router.get("/families/{family_id}/applications", response_model=List[ApplicationResponseSchema])
def list_applications(family_id: str, db: Session = Depends(get_db), current_user: UserAccount = Depends(get_current_user)):
    _authorize_family(db, family_id, current_user)
    applications = db.query(SchemeApplication).filter(SchemeApplication.family_id == family_id).order_by(SchemeApplication.submitted_at.desc()).all()
    return [_response(application) for application in applications]


@router.post("/families/{family_id}/applications/{application_id}/refresh", response_model=ApplicationResponseSchema)
def refresh_application_status(family_id: str, application_id: str, db: Session = Depends(get_db), current_user: UserAccount = Depends(get_current_user)):
    _authorize_family(db, family_id, current_user)
    application = db.query(SchemeApplication).filter(SchemeApplication.application_id == application_id, SchemeApplication.family_id == family_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found.")
    application = refresh_application(db, application)
    write_audit(db, current_user.user_id, current_user.role.value, "REFRESH_APPLICATION", "scheme_application", application.application_id, family_id, purpose="Application status refresh")
    return _response(application)
