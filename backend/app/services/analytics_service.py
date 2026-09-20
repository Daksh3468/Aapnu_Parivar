"""
analytics_service.py
====================
Computes and refreshes statewide welfare KPIs.
Drives the Disbursement Simulation engine (DBT-style projection).

All simulation operations are READ-ONLY and never mutate citizen data.
"""
from __future__ import annotations

import random
import string
import uuid
from datetime import date, datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.analytics import AnalyticsDailySnapshot, DisbursementSimulationRun
from app.models.application import SchemeApplication
from app.models.enums import (
    ApplicationStatusEnum,
    FamilyStatusEnum,
    IncomeBandEnum,
    LifeEventTypeEnum,
    RationCardTypeEnum,
)
from app.models.family import Family
from app.models.life_event import LifeEventRecord
from app.models.membership import FamilyMembership


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _count(db: Session, model, **filters) -> int:
    q = db.query(model)
    for attr, val in filters.items():
        q = q.filter(getattr(model, attr) == val)
    return q.count()


def _scheme_application_counts(db: Session) -> Dict[str, int]:
    from app.models.scheme import Scheme
    rows = (
        db.query(Scheme.name, SchemeApplication.status)
        .join(SchemeApplication, SchemeApplication.scheme_id == Scheme.scheme_id)
        .all()
    )
    counts: Dict[str, int] = {}
    for scheme_name, _ in rows:
        counts[scheme_name] = counts.get(scheme_name, 0) + 1
    return counts


def _district_breakdown(db: Session) -> Dict[str, Dict]:
    """Compute per-district family and disbursement breakdown."""
    from app.models.address import Address
    from app.models.district import District
    from app.models.scheme import Scheme

    # Family count per district
    rows = (
        db.query(District.name, Family.family_id)
        .join(Address, Family.address_id == Address.address_id)
        .join(District, Address.district_code == District.district_code)
        .all()
    )
    breakdown: Dict[str, Dict] = {}
    seen_families: set = set()
    for dist_name, fam_id in rows:
        if dist_name not in breakdown:
            breakdown[dist_name] = {"families": 0, "disbursed_inr": 0.0}
        if fam_id not in seen_families:
            breakdown[dist_name]["families"] += 1
            seen_families.add(fam_id)

    # Disbursement totals: no monetary field in schema yet — disburse_inr remains 0.0

    return breakdown


def _monthly_trend(db: Session) -> List[Dict]:
    """
    Return last 12 months of application + disbursement data.
    Uses Python grouping; for large datasets a SQL GROUP BY would be better.
    """
    from app.models.scheme import Scheme
    from collections import defaultdict

    apps = db.query(
        SchemeApplication.submitted_at,
        SchemeApplication.status,
    ).all()

    monthly: Dict[str, Dict] = defaultdict(lambda: {"applications": 0, "disbursed_inr": 0.0})
    for submitted_at, status in apps:
        if submitted_at is None:
            continue
        key = submitted_at.strftime("%Y-%m")
        monthly[key]["applications"] += 1
        # No monetary amount in schema yet — count disbursed as applications
        if status == ApplicationStatusEnum.DISBURSED:
            monthly[key]["disbursed_inr"] += 0.0

    return [
        {"month": k, "applications": v["applications"], "disbursed_inr": v["disbursed_inr"]}
        for k, v in sorted(monthly.items())
    ][-12:]  # last 12 months


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def refresh_daily_snapshot(db: Session) -> AnalyticsDailySnapshot:
    """
    Recompute today's aggregate snapshot and upsert it into the DB.
    Called on-demand from the analytics API or a nightly cron.
    """
    today = date.today()

    # --- Raw counts ---
    total_families = db.query(Family).count()
    active_families = _count(db, Family, status=FamilyStatusEnum.VERIFIED)
    total_members = db.query(FamilyMembership).filter(
        FamilyMembership.end_date.is_(None)
    ).count()
    bpl_families = (
        db.query(Family)
        .filter(Family.ration_card_type.in_([RationCardTypeEnum.AAY, RationCardTypeEnum.PHH]))
        .count()
    )
    verified_families = _count(db, Family, status=FamilyStatusEnum.VERIFIED)

    total_apps = db.query(SchemeApplication).count()
    approved_apps = _count(db, SchemeApplication, status=ApplicationStatusEnum.APPROVED)
    disbursed_apps = _count(db, SchemeApplication, status=ApplicationStatusEnum.DISBURSED)
    rejected_apps = _count(db, SchemeApplication, status=ApplicationStatusEnum.REJECTED)
    pending_apps = _count(db, SchemeApplication, status=ApplicationStatusEnum.SUBMITTED)

    # No monetary field in schema yet — disbursement count as proxy
    total_disbursed_inr = 0.0

    # Life-event counts
    births = _count(db, LifeEventRecord, event_type=LifeEventTypeEnum.BIRTH)
    deaths = _count(db, LifeEventRecord, event_type=LifeEventTypeEnum.DEATH)
    splits = _count(db, LifeEventRecord, event_type=LifeEventTypeEnum.HOUSEHOLD_SPLIT)

    # Complex aggregations
    district_breakdown = _district_breakdown(db)
    scheme_counts = _scheme_application_counts(db)
    trend = _monthly_trend(db)

    # Upsert
    snapshot = db.query(AnalyticsDailySnapshot).filter(
        AnalyticsDailySnapshot.snapshot_date == today
    ).first()

    if not snapshot:
        snapshot = AnalyticsDailySnapshot(id=str(uuid.uuid4()), snapshot_date=today)
        db.add(snapshot)

    snapshot.total_families = total_families
    snapshot.active_families = active_families
    snapshot.total_members = total_members
    snapshot.verified_families = verified_families
    snapshot.bpl_families = bpl_families
    snapshot.total_scheme_applications = total_apps
    snapshot.approved_applications = approved_apps
    snapshot.disbursed_applications = disbursed_apps
    snapshot.rejected_applications = rejected_apps
    snapshot.pending_applications = pending_apps
    snapshot.total_disbursed_amount_inr = total_disbursed_inr
    snapshot.total_births_recorded = births
    snapshot.total_deaths_recorded = deaths
    snapshot.total_splits_this_month = splits
    snapshot.district_breakdown_json = district_breakdown
    snapshot.scheme_application_counts_json = scheme_counts
    snapshot.monthly_trend_json = trend
    snapshot.refreshed_at = datetime.utcnow()

    db.commit()
    db.refresh(snapshot)
    return snapshot


def get_latest_snapshot(db: Session) -> Optional[AnalyticsDailySnapshot]:
    """Return most recent snapshot (refreshes today if none exists)."""
    today = date.today()
    snapshot = db.query(AnalyticsDailySnapshot).order_by(
        AnalyticsDailySnapshot.snapshot_date.desc()
    ).first()
    if snapshot is None or snapshot.snapshot_date < today:
        snapshot = refresh_daily_snapshot(db)
    return snapshot


# ---------------------------------------------------------------------------
# Disbursement Simulation Engine
# ---------------------------------------------------------------------------

def _generate_run_id() -> str:
    suffix = "".join(random.choices(string.digits, k=4))
    return f"SIM-{date.today().strftime('%Y%m%d')}-{suffix}"


def run_disbursement_simulation(
    db: Session,
    simulation_label: str,
    benefit_amount_inr: float,
    scheme_filter: Optional[str] = None,
    income_band_filter: Optional[str] = None,
    ration_card_filter: Optional[str] = None,
    triggered_by_user_id: Optional[str] = None,
) -> DisbursementSimulationRun:
    """
    Project welfare disbursement across eligible families.
    READ-ONLY – never modifies citizen data.

    Eligibility criteria applied:
      - Family status = VERIFIED
      - Optional income band filter
      - Optional ration card type filter
      - Optional scheme name filter (cross-referenced via SchemeApplication)
    """
    from app.models.address import Address
    from app.models.district import District
    from app.models.scheme import Scheme

    try:
        # Base query: verified families
        query = db.query(Family).filter(Family.status == FamilyStatusEnum.VERIFIED)

        if income_band_filter:
            try:
                query = query.filter(Family.income_band == IncomeBandEnum(income_band_filter))
            except ValueError:
                pass

        if ration_card_filter:
            try:
                query = query.filter(Family.ration_card_type == RationCardTypeEnum(ration_card_filter))
            except ValueError:
                pass

        if scheme_filter:
            scheme = db.query(Scheme).filter(Scheme.name.ilike(f"%{scheme_filter}%")).first()
            if scheme:
                scheme_family_ids = db.query(SchemeApplication.family_id).filter(
                    SchemeApplication.scheme_id == scheme.scheme_id
                ).subquery()
                query = query.filter(Family.family_id.in_(scheme_family_ids))

        families: List[Family] = query.all()
        eligible_count = len(families)
        total_projected = eligible_count * benefit_amount_inr

        # District-level breakdown
        district_breakdown: Dict[str, Any] = {}
        for family in families:
            address = db.query(Address).filter(Address.address_id == family.address_id).first()
            if address:
                district = db.query(District).filter(District.district_code == address.district_code).first()
                district_name = district.name if district else "Unknown"
            else:
                district_name = "Unknown"

            if district_name not in district_breakdown:
                district_breakdown[district_name] = {"count": 0, "amount_inr": 0.0}
            district_breakdown[district_name]["count"] += 1
            district_breakdown[district_name]["amount_inr"] += benefit_amount_inr

        # Scheme breakdown (count of approved apps per scheme for eligible families)
        family_ids = [f.family_id for f in families]
        scheme_breakdown: Dict[str, Any] = {}
        if family_ids:
            scheme_rows = (
                db.query(Scheme.name, SchemeApplication.family_id)
                .join(SchemeApplication, SchemeApplication.scheme_id == Scheme.scheme_id)
                .filter(SchemeApplication.family_id.in_(family_ids))
                .all()
            )
            for s_name, _ in scheme_rows:
                scheme_breakdown[s_name] = scheme_breakdown.get(s_name, 0) + 1

        run = DisbursementSimulationRun(
            id=str(uuid.uuid4()),
            run_id=_generate_run_id(),
            simulation_label=simulation_label,
            scheme_filter=scheme_filter,
            income_band_filter=income_band_filter,
            ration_card_filter=ration_card_filter,
            benefit_amount_inr=benefit_amount_inr,
            simulation_date=date.today(),
            eligible_family_count=eligible_count,
            total_projected_disbursement_inr=total_projected,
            district_breakdown_json=district_breakdown,
            scheme_breakdown_json=scheme_breakdown,
            triggered_by_user_id=triggered_by_user_id,
            status="COMPLETED",
        )
        db.add(run)
        db.commit()
        db.refresh(run)
        return run

    except Exception as exc:
        db.rollback()
        run = DisbursementSimulationRun(
            id=str(uuid.uuid4()),
            run_id=_generate_run_id(),
            simulation_label=simulation_label,
            benefit_amount_inr=benefit_amount_inr,
            simulation_date=date.today(),
            triggered_by_user_id=triggered_by_user_id,
            status="FAILED",
            error_message=str(exc),
        )
        db.add(run)
        db.commit()
        db.refresh(run)
        return run


def list_simulation_runs(db: Session, limit: int = 20) -> List[DisbursementSimulationRun]:
    return (
        db.query(DisbursementSimulationRun)
        .order_by(DisbursementSimulationRun.created_at.desc())
        .limit(limit)
        .all()
    )
