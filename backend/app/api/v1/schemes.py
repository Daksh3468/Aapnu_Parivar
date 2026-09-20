from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.db import get_db
from app.models.scheme import Scheme, SchemeCategory, SchemeLevelEnum, BenefitTypeEnum, EligibilityUnitEnum
from app.schemas.scheme import SchemeResponseSchema, CategoryResponseSchema
from app.services.sync_service import sync_all_schemes_and_categories
from app.connectors.registry import connector_registry

router = APIRouter()


def _build_scheme_dto(scheme: Scheme) -> SchemeResponseSchema:
    return SchemeResponseSchema(
        scheme_id=scheme.scheme_id,
        code=scheme.code,
        name=scheme.name,
        short_description=scheme.short_description,
        benefit_summary=scheme.benefit_summary,
        level=scheme.level.value,
        department=scheme.department,
        category_id=scheme.category_id,
        category_name=scheme.category.name if scheme.category else None,
        benefit_type=scheme.benefit_type.value,
        eligibility_unit=scheme.eligibility_unit.value,
        target_groups=scheme.target_groups or [],
        official_url=scheme.official_url,
        require_officer_confirmation_before_apply=scheme.require_officer_confirmation_before_apply,
        source_system=scheme.source_system,
        last_synced_at=scheme.last_synced_at.strftime("%Y-%m-%d %H:%M:%S") if scheme.last_synced_at else "",
    )


@router.get("/schemes/categories", response_model=List[CategoryResponseSchema])
def get_categories(db: Session = Depends(get_db)):
    """Retrieve list of scheme categories."""
    categories = db.query(SchemeCategory).order_by(SchemeCategory.category_id).all()
    if not categories:
        sync_all_schemes_and_categories(db)
        categories = db.query(SchemeCategory).order_by(SchemeCategory.category_id).all()

    return categories


@router.get("/schemes", response_model=List[SchemeResponseSchema])
def get_schemes(
    level: Optional[str] = Query(None, description="Filter by CENTRAL or STATE"),
    category_id: Optional[int] = Query(None, description="Filter by Category ID"),
    department: Optional[str] = Query(None, description="Filter by Department"),
    benefit_type: Optional[str] = Query(None, description="Filter by CASH, IN_KIND, INSURANCE, SUBSIDY, LOAN, SERVICE"),
    eligibility_unit: Optional[str] = Query(None, description="Filter by FAMILY or INDIVIDUAL"),
    search: Optional[str] = Query(None, description="Text search by name or description"),
    db: Session = Depends(get_db),
):
    """
    Search and filter master scheme catalog across Central and Gujarat Government schemes.
    """
    # Ensure fixture data is initialized if empty
    count = db.query(Scheme).count()
    if count == 0:
        sync_all_schemes_and_categories(db)

    query = db.query(Scheme).filter(Scheme.is_active.is_(True))

    if level:
        query = query.filter(Scheme.level == SchemeLevelEnum(level.upper()))
    if category_id:
        query = query.filter(Scheme.category_id == category_id)
    if department:
        query = query.filter(Scheme.department.ilike(f"%{department}%"))
    if benefit_type:
        query = query.filter(Scheme.benefit_type == BenefitTypeEnum(benefit_type.upper()))
    if eligibility_unit:
        query = query.filter(Scheme.eligibility_unit == EligibilityUnitEnum(eligibility_unit.upper()))
    if search:
        s = f"%{search.strip()}%"
        query = query.filter(or_(Scheme.name.ilike(s), Scheme.short_description.ilike(s), Scheme.code.ilike(s)))

    schemes = query.order_by(Scheme.category_id, Scheme.name).all()
    return [_build_scheme_dto(s) for s in schemes]


@router.get("/schemes/{code}", response_model=SchemeResponseSchema)
def get_scheme_by_code(code: str, db: Session = Depends(get_db)):
    """Retrieve detailed scheme information by scheme code (e.g. PMKISAN, MA_AMRUTAM)."""
    scheme = db.query(Scheme).filter(Scheme.code == code.strip().upper()).first()
    if not scheme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scheme with code '{code}' not found.",
        )
    return _build_scheme_dto(scheme)


@router.post("/connectors/sync")
def trigger_connector_sync(db: Session = Depends(get_db)):
    """On-demand departmental connector synchronization."""
    synced_count = sync_all_schemes_and_categories(db)
    return {
        "message": f"Successfully synchronized {synced_count} schemes from departmental connectors.",
        "synced_count": synced_count,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/connectors/health")
def get_connectors_health():
    """Get status and latency of departmental connectors."""
    return connector_registry.get_health_all()
