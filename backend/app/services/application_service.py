import hashlib
import secrets
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.connectors.registry import connector_registry
from app.models.application import ApplicationStatusHistory, SchemeApplication
from app.models.enums import ApplicationStatusEnum, EligibilityStatusEnum
from app.models.family import Family
from app.models.scheme import Scheme
from app.services.eligibility_service import EligibilityEngine


ACTIVE_APPLICATION_STATUSES = {
    ApplicationStatusEnum.SUBMITTED,
    ApplicationStatusEnum.UNDER_REVIEW,
    ApplicationStatusEnum.APPROVED,
}
ELIGIBLE_STATUSES = {EligibilityStatusEnum.AUTO_ELIGIBLE, EligibilityStatusEnum.OFFICER_APPROVED}
STATUS_ORDER = {
    ApplicationStatusEnum.SUBMITTED: 0,
    ApplicationStatusEnum.UNDER_REVIEW: 1,
    ApplicationStatusEnum.APPROVED: 2,
    ApplicationStatusEnum.DISBURSED: 3,
}


def _applicant_token(family_id: str) -> str:
    """Stable synthetic portal token; never expose household data to a connector."""
    return hashlib.sha256(f"demo-application:{family_id}".encode()).hexdigest()[:32]


def _external_reference(source_system: str) -> str:
    prefix = "DG" if source_system == "DIGITAL_GUJARAT" else "JS"
    return f"{prefix}-2026-APP-{secrets.randbelow(90000) + 10000}"


def _append_history(db: Session, application: SchemeApplication, app_status: ApplicationStatusEnum, message: str, source_system: str, metadata: dict | None = None) -> None:
    db.add(ApplicationStatusHistory(
        application_id=application.application_id,
        status=app_status,
        source_system=source_system,
        message=message,
        metadata_json=metadata,
    ))


def create_application(db: Session, family: Family, scheme: Scheme, applicant_person_id: str | None = None) -> SchemeApplication:
    eligibility = next(
        (item for item in EligibilityEngine.evaluate_all_schemes_for_family(db, family.family_id) if item.scheme_id == scheme.scheme_id),
        None,
    )
    if not eligibility or eligibility.status not in ELIGIBLE_STATUSES:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="This household is not currently eligible to apply for this scheme.")

    existing = db.query(SchemeApplication).filter(
        SchemeApplication.family_id == family.family_id,
        SchemeApplication.scheme_id == scheme.scheme_id,
        SchemeApplication.status.in_(ACTIVE_APPLICATION_STATUSES),
    ).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An active application already exists for this scheme.")

    application = SchemeApplication(
        family_id=family.family_id,
        scheme_id=scheme.scheme_id,
        applicant_person_id=applicant_person_id,
        applicant_token=_applicant_token(family.family_id),
        source_system=scheme.source_system,
        external_reference=_external_reference(scheme.source_system),
        official_url=scheme.official_url,
        status=ApplicationStatusEnum.SUBMITTED,
        payload_snapshot={"family_id": family.family_id, "scheme_code": scheme.code, "demo": True},
    )
    db.add(application)
    db.flush()
    _append_history(db, application, ApplicationStatusEnum.SUBMITTED, "Application created and securely handed off to the official portal simulation.", application.source_system)
    db.commit()
    db.refresh(application)
    return application


def refresh_application(db: Session, application: SchemeApplication) -> SchemeApplication:
    connector = connector_registry.get_connector(application.source_system)
    if not connector:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="The application source portal is unavailable.")

    updates = connector.fetch_application_status(application.applicant_token, application.external_reference)
    if not updates:
        application.last_synced_at = datetime.utcnow()
        db.commit()
        return application

    update = updates[-1]
    try:
        new_status = ApplicationStatusEnum(update["status"])
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="The source portal returned an invalid status.") from exc

    current_order = STATUS_ORDER.get(application.status, -1)
    new_order = STATUS_ORDER.get(new_status, -1)
    if new_status == ApplicationStatusEnum.REJECTED or new_order >= current_order:
        if new_status != application.status:
            application.status = new_status
            _append_history(
                db,
                application,
                new_status,
                "Status refreshed from the official portal simulation.",
                update.get("source_system", application.source_system),
                {"external_reference": application.external_reference},
            )
    application.last_synced_at = datetime.utcnow()
    db.commit()
    db.refresh(application)
    return application
