from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.auth_deps import get_current_user
from app.core.jurisdiction import build_officer_jurisdiction_scope, apply_family_jurisdiction_filter
from app.models.user import UserAccount
from app.models.family import Family
from app.models.person import Person
from app.models.enums import UserRoleEnum, LifeEventTypeEnum, SplitStatusEnum
from app.models.life_event import LifeEventRecord, FamilySplitRecord
from app.schemas.life_event import (
    LifeEventCreateSchema,
    LifeEventResponseSchema,
    FamilySplitRequestSchema,
    FamilySplitResponseSchema,
    OfficerSplitReviewSchema,
)
from app.services.life_event_service import LifeEventService
from app.services.audit_service import write_audit

router = APIRouter(tags=["Life Events & Family Lineage Engine"])


@router.get("/families/{family_id}/life-events", response_model=List[LifeEventResponseSchema])
def list_family_life_events(
    family_id: str,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Retrieves the immutable timeline of life events for a given household.
    """
    family = db.query(Family).filter(Family.family_id == family_id).first()
    if not family:
        raise HTTPException(status_code=404, detail="Family not found")

    scope = build_officer_jurisdiction_scope(current_user)
    if current_user.role not in [UserRoleEnum.CITIZEN_HEAD, UserRoleEnum.CITIZEN_MEMBER]:
        scoped_q = apply_family_jurisdiction_filter(db.query(Family).filter(Family.family_id == family_id), scope)
        if not scoped_q.first():
            raise HTTPException(status_code=403, detail="Family is out of officer jurisdiction scope")

    events = db.query(LifeEventRecord).filter(LifeEventRecord.family_id == family_id).order_by(LifeEventRecord.created_at.desc()).all()

    res = []
    for evt in events:
        p_name = evt.person.full_name if evt.person else None
        res.append(
            LifeEventResponseSchema(
                event_id=evt.event_id,
                family_id=evt.family_id,
                person_id=evt.person_id,
                person_name=p_name,
                event_type=evt.event_type.value,
                event_date=evt.event_date,
                description=evt.description,
                details_json=evt.details_json,
                created_at=evt.created_at.isoformat(),
            )
        )

    return res



@router.post("/families/{family_id}/life-events", response_model=LifeEventResponseSchema, status_code=status.HTTP_201_CREATED)
def register_life_event(
    family_id: str,
    payload: LifeEventCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Registers a new household life event (Birth, Death, Marriage, Address Change).
    """
    family = db.query(Family).filter(Family.family_id == family_id).first()
    if not family:
        raise HTTPException(status_code=404, detail="Family not found")

    # If death event, verify person and set inactive
    if payload.event_type == LifeEventTypeEnum.DEATH and payload.person_id:
        person = db.query(Person).filter(Person.person_id == payload.person_id).first()
        if person:
            person.is_active = False

    evt = LifeEventRecord(
        family_id=family_id,
        person_id=payload.person_id,
        event_type=payload.event_type,
        event_date=payload.event_date,
        description=payload.description or f"Registered {payload.event_type.value} life event",
        details_json=payload.details,
        registered_by_user_id=current_user.user_id,
    )
    db.add(evt)
    db.commit()
    db.refresh(evt)

    write_audit(
        db=db,
        actor_user_id=str(current_user.user_id),
        actor_role=current_user.role.value,
        action="LIFE_EVENT_REGISTER",
        entity_type="life_event",
        entity_id=str(evt.event_id),
        family_id=family_id,
        details={"event_type": payload.event_type.value},
    )

    p_name = evt.person.full_name if evt.person else None
    return LifeEventResponseSchema(

        event_id=evt.event_id,
        family_id=evt.family_id,
        person_id=evt.person_id,
        person_name=p_name,
        event_type=evt.event_type.value,
        event_date=evt.event_date,
        description=evt.description,
        details_json=evt.details_json,
        created_at=evt.created_at.isoformat(),
    )


@router.post("/families/{family_id}/split", response_model=FamilySplitResponseSchema)
def request_family_split(
    family_id: str,
    payload: FamilySplitRequestSchema,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Submits a household split request. Performs anomaly risk evaluation.
    If anomaly score <= 50, split is automatically executed.
    If anomaly score > 50, split is placed into officer review queue (PENDING_OFFICER_REVIEW).
    """
    family = db.query(Family).filter(Family.family_id == family_id).first()
    if not family:
        raise HTTPException(status_code=404, detail="Family not found")

    # Evaluate anomaly risk score
    anomaly_score, risk_flags = LifeEventService.calculate_split_anomaly_score(
        db=db,
        source_family_id=family_id,
        moved_person_ids=payload.moved_person_ids,
        split_reason=payload.split_reason,
    )

    status_val = SplitStatusEnum.AUTOMATICALLY_APPROVED if anomaly_score <= 50 else SplitStatusEnum.PENDING_OFFICER_REVIEW

    split_rec = FamilySplitRecord(
        source_family_id=family_id,
        requested_by_user_id=current_user.user_id,
        moved_person_ids_json=payload.moved_person_ids,
        new_head_person_id=payload.new_head_person_id,
        replacement_source_head_person_id=payload.replacement_source_head_person_id,
        split_reason=payload.split_reason,
        anomaly_score=anomaly_score,
        anomaly_reasons_json=risk_flags,
        status=status_val,
    )
    db.add(split_rec)
    db.commit()
    db.refresh(split_rec)

    # If low risk, execute immediately
    if status_val == SplitStatusEnum.AUTOMATICALLY_APPROVED:
        new_addr_dict = payload.new_address.model_dump() if payload.new_address else None
        LifeEventService.execute_family_split(
            db=db,
            split_record=split_rec,
            actor_user_id=current_user.user_id,
            actor_role=current_user.role.value,
            new_address_dict=new_addr_dict,
        )

    return FamilySplitResponseSchema(
        split_id=split_rec.split_id,
        source_family_id=split_rec.source_family_id,
        new_family_id=split_rec.new_family_id,
        requested_by_user_id=split_rec.requested_by_user_id,
        moved_person_ids=split_rec.moved_person_ids_json or [],
        new_head_person_id=split_rec.new_head_person_id,
        split_reason=split_rec.split_reason,
        anomaly_score=split_rec.anomaly_score,
        anomaly_reasons=split_rec.anomaly_reasons_json or [],
        status=split_rec.status.value,
        officer_notes=split_rec.officer_notes,
        created_at=split_rec.created_at.isoformat() if split_rec.created_at else datetime.utcnow().isoformat(),
    )


@router.get("/officer/splits-queue", response_model=List[FamilySplitResponseSchema])
def get_officer_splits_queue(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Retrieves pending household split requests requiring officer approval within jurisdiction.
    """
    if current_user.role in [UserRoleEnum.CITIZEN_HEAD, UserRoleEnum.CITIZEN_MEMBER]:
        raise HTTPException(status_code=403, detail="Citizens cannot access officer split review queues")

    scope = build_officer_jurisdiction_scope(current_user)
    scoped_families = apply_family_jurisdiction_filter(db.query(Family), scope).all()
    scoped_family_ids = [f.family_id for f in scoped_families]

    splits = db.query(FamilySplitRecord).filter(
        FamilySplitRecord.source_family_id.in_(scoped_family_ids),
        FamilySplitRecord.status == SplitStatusEnum.PENDING_OFFICER_REVIEW,
    ).all()

    return [
        FamilySplitResponseSchema(
            split_id=s.split_id,
            source_family_id=s.source_family_id,
            new_family_id=s.new_family_id,
            requested_by_user_id=s.requested_by_user_id,
            moved_person_ids=s.moved_person_ids_json or [],
            new_head_person_id=s.new_head_person_id,
            split_reason=s.split_reason,
            anomaly_score=s.anomaly_score,
            anomaly_reasons=s.anomaly_reasons_json or [],
            status=s.status.value,
            officer_notes=s.officer_notes,
            created_at=s.created_at.isoformat() if s.created_at else datetime.utcnow().isoformat(),
        )
        for s in splits
    ]


@router.post("/officer/splits/{split_id}/review", response_model=FamilySplitResponseSchema)
def review_family_split(
    split_id: int,
    payload: OfficerSplitReviewSchema,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Department Officer endpoint to approve or reject a pending household split request.
    """
    if current_user.role in [UserRoleEnum.CITIZEN_HEAD, UserRoleEnum.CITIZEN_MEMBER]:
        raise HTTPException(status_code=403, detail="Citizens cannot review split requests")

    split_rec = db.query(FamilySplitRecord).filter(FamilySplitRecord.split_id == split_id).first()
    if not split_rec:
        raise HTTPException(status_code=404, detail="Household split record not found")

    scope = build_officer_jurisdiction_scope(current_user)
    scoped_q = apply_family_jurisdiction_filter(
        db.query(Family).filter(Family.family_id == split_rec.source_family_id),
        scope
    )
    if not scoped_q.first():
        raise HTTPException(status_code=403, detail="Household is out of officer jurisdiction scope")

    if payload.status == SplitStatusEnum.OFFICER_APPROVED:
        LifeEventService.execute_family_split(
            db=db,
            split_record=split_rec,
            actor_user_id=current_user.user_id,
            actor_role=current_user.role.value,
        )
        split_rec.status = SplitStatusEnum.OFFICER_APPROVED
    else:
        split_rec.status = SplitStatusEnum.OFFICER_REJECTED

    split_rec.reviewed_by_user_id = current_user.user_id
    split_rec.reviewed_at = datetime.utcnow()
    split_rec.officer_notes = payload.officer_notes
    db.commit()

    return FamilySplitResponseSchema(
        split_id=split_rec.split_id,
        source_family_id=split_rec.source_family_id,
        new_family_id=split_rec.new_family_id,
        requested_by_user_id=split_rec.requested_by_user_id,
        moved_person_ids=split_rec.moved_person_ids_json or [],
        new_head_person_id=split_rec.new_head_person_id,
        split_reason=split_rec.split_reason,
        anomaly_score=split_rec.anomaly_score,
        anomaly_reasons=split_rec.anomaly_reasons_json or [],
        status=split_rec.status.value,
        officer_notes=split_rec.officer_notes,
        created_at=split_rec.created_at.isoformat() if split_rec.created_at else datetime.utcnow().isoformat(),
    )
