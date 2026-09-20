"""
analytics.py – FastAPI router for the State Analytics Dashboard and
Disbursement Simulation endpoints.

Routes (all under /api/v1):
  GET  /analytics/overview          – latest KPI snapshot (refreshes if stale)
  POST /analytics/refresh           – force-refresh today's snapshot
  GET  /analytics/simulations       – list past simulation runs
  POST /analytics/simulate          – run a new disbursement simulation
  GET  /analytics/simulations/{run_id} – fetch a specific simulation result
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.auth_deps import get_current_user
from app.models.user import UserAccount
from app.services import analytics_service

router = APIRouter(prefix="/analytics", tags=["State Analytics Dashboard"])


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class OverviewResponse(BaseModel):
    snapshot_date: str
    total_families: int
    active_families: int
    total_members: int
    verified_families: int
    bpl_families: int
    total_scheme_applications: int
    approved_applications: int
    disbursed_applications: int
    rejected_applications: int
    pending_applications: int
    total_disbursed_amount_inr: float
    total_births_recorded: int
    total_deaths_recorded: int
    total_splits_this_month: int
    district_breakdown: Dict[str, Any]
    scheme_application_counts: Dict[str, int]
    monthly_trend: List[Dict[str, Any]]
    refreshed_at: Optional[str]

    class Config:
        from_attributes = True


class SimulationRequest(BaseModel):
    simulation_label: str = Field(..., min_length=3, max_length=200, example="PM-KISAN Q1 2025 Projection")
    benefit_amount_inr: float = Field(..., gt=0, example=6000.0)
    scheme_filter: Optional[str] = Field(None, example="Kisan Samman")
    income_band_filter: Optional[str] = Field(None, example="LT_1L")
    ration_card_filter: Optional[str] = Field(None, example="AAY")


class SimulationResponse(BaseModel):
    run_id: str
    simulation_label: str
    simulation_date: str
    benefit_amount_inr: float
    scheme_filter: Optional[str]
    income_band_filter: Optional[str]
    ration_card_filter: Optional[str]
    eligible_family_count: int
    total_projected_disbursement_inr: float
    district_breakdown: Optional[Dict[str, Any]]
    scheme_breakdown: Optional[Dict[str, Any]]
    status: str
    error_message: Optional[str]
    created_at: str

    class Config:
        from_attributes = True


def _format_snapshot(snap) -> OverviewResponse:
    return OverviewResponse(
        snapshot_date=str(snap.snapshot_date),
        total_families=snap.total_families or 0,
        active_families=snap.active_families or 0,
        total_members=snap.total_members or 0,
        verified_families=snap.verified_families or 0,
        bpl_families=snap.bpl_families or 0,
        total_scheme_applications=snap.total_scheme_applications or 0,
        approved_applications=snap.approved_applications or 0,
        disbursed_applications=snap.disbursed_applications or 0,
        rejected_applications=snap.rejected_applications or 0,
        pending_applications=snap.pending_applications or 0,
        total_disbursed_amount_inr=snap.total_disbursed_amount_inr or 0.0,
        total_births_recorded=snap.total_births_recorded or 0,
        total_deaths_recorded=snap.total_deaths_recorded or 0,
        total_splits_this_month=snap.total_splits_this_month or 0,
        district_breakdown=snap.district_breakdown_json or {},
        scheme_application_counts=snap.scheme_application_counts_json or {},
        monthly_trend=snap.monthly_trend_json or [],
        refreshed_at=str(snap.refreshed_at) if snap.refreshed_at else None,
    )


def _format_simulation(run) -> SimulationResponse:
    return SimulationResponse(
        run_id=run.run_id,
        simulation_label=run.simulation_label,
        simulation_date=str(run.simulation_date),
        benefit_amount_inr=run.benefit_amount_inr,
        scheme_filter=run.scheme_filter,
        income_band_filter=run.income_band_filter,
        ration_card_filter=run.ration_card_filter,
        eligible_family_count=run.eligible_family_count or 0,
        total_projected_disbursement_inr=run.total_projected_disbursement_inr or 0.0,
        district_breakdown=run.district_breakdown_json,
        scheme_breakdown=run.scheme_breakdown_json,
        status=run.status,
        error_message=run.error_message,
        created_at=str(run.created_at),
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/overview", response_model=OverviewResponse, summary="Get latest KPI snapshot")
def get_overview(
    db: Session = Depends(get_db),
):
    """
    Returns the latest pre-computed statewide welfare KPI snapshot.
    If today's snapshot is missing, it is computed on-the-fly.
    Open to all authenticated users (no role restriction – public KPIs).
    """
    snap = analytics_service.get_latest_snapshot(db)
    if snap is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Could not compute analytics snapshot.")
    return _format_snapshot(snap)


@router.post("/refresh", response_model=OverviewResponse, summary="Force-refresh today's analytics snapshot")
def force_refresh(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """Force re-computation of today's analytics snapshot. Officers and above only."""
    from app.models.enums import UserRoleEnum
    if current_user.role not in (
        UserRoleEnum.FIELD_OFFICER,
        UserRoleEnum.DISTRICT_OFFICER,
        UserRoleEnum.STATE_ADMIN,
        UserRoleEnum.AUDITOR,
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role to refresh analytics.")
    snap = analytics_service.refresh_daily_snapshot(db)
    return _format_snapshot(snap)


@router.get("/simulations", response_model=List[SimulationResponse], summary="List past simulation runs")
def list_simulations(
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """List the most recent disbursement simulation runs (officer+ access)."""
    from app.models.enums import UserRoleEnum
    if current_user.role not in (
        UserRoleEnum.FIELD_OFFICER,
        UserRoleEnum.DISTRICT_OFFICER,
        UserRoleEnum.STATE_ADMIN,
        UserRoleEnum.AUDITOR,
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role.")
    runs = analytics_service.list_simulation_runs(db, limit=min(limit, 100))
    return [_format_simulation(r) for r in runs]


@router.post("/simulate", response_model=SimulationResponse, summary="Run disbursement simulation")
def run_simulation(
    req: SimulationRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """
    Project welfare disbursement across eligible families.
    READ-ONLY — never mutates citizen data.
    Requires DISTRICT_OFFICER or STATE_ADMIN role.
    """
    from app.models.enums import UserRoleEnum
    if current_user.role not in (
        UserRoleEnum.DISTRICT_OFFICER,
        UserRoleEnum.STATE_ADMIN,
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only District Officers and State Admins may run simulations.")

    run = analytics_service.run_disbursement_simulation(
        db=db,
        simulation_label=req.simulation_label,
        benefit_amount_inr=req.benefit_amount_inr,
        scheme_filter=req.scheme_filter,
        income_band_filter=req.income_band_filter,
        ration_card_filter=req.ration_card_filter,
        triggered_by_user_id=str(current_user.user_id),
    )
    return _format_simulation(run)


@router.get("/simulations/{run_id}", response_model=SimulationResponse, summary="Get simulation result by run ID")
def get_simulation(
    run_id: str,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user),
):
    """Fetch a specific simulation result by its run ID (e.g., SIM-20240915-0012)."""
    from app.models.analytics import DisbursementSimulationRun
    from app.models.enums import UserRoleEnum
    if current_user.role not in (
        UserRoleEnum.FIELD_OFFICER,
        UserRoleEnum.DISTRICT_OFFICER,
        UserRoleEnum.STATE_ADMIN,
        UserRoleEnum.AUDITOR,
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role.")
    run = db.query(DisbursementSimulationRun).filter(DisbursementSimulationRun.run_id == run_id).first()
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Simulation run '{run_id}' not found.")
    return _format_simulation(run)
