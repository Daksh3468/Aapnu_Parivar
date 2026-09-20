"""
Analytics and Disbursement Simulation models.

AnalyticsDailySnapshot  – pre-aggregated welfare metrics persisted once per day
DisbursementSimulationRun – immutable audit record of each simulation execution
"""
from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import Column, Date, DateTime, Float, Integer, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID

from app.core.db import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class AnalyticsDailySnapshot(Base):
    """
    One row per calendar day capturing statewide welfare KPIs.
    Populated by the analytics_service refresh job (or a future DBT run).
    """
    __tablename__ = "analytics_daily_snapshot"

    id = Column(String(36), primary_key=True, default=_uuid)
    snapshot_date = Column(Date, nullable=False, unique=True, index=True)

    # Household metrics
    total_families = Column(Integer, default=0)
    active_families = Column(Integer, default=0)
    total_members = Column(Integer, default=0)
    verified_families = Column(Integer, default=0)
    bpl_families = Column(Integer, default=0)

    # Scheme metrics
    total_scheme_applications = Column(Integer, default=0)
    approved_applications = Column(Integer, default=0)
    disbursed_applications = Column(Integer, default=0)
    rejected_applications = Column(Integer, default=0)
    pending_applications = Column(Integer, default=0)

    # Disbursement financials (INR)
    total_disbursed_amount_inr = Column(Float, default=0.0)

    # Life-event metrics
    total_births_recorded = Column(Integer, default=0)
    total_deaths_recorded = Column(Integer, default=0)
    total_splits_this_month = Column(Integer, default=0)

    # District-level breakdown (JSON: {district_name: {families: int, disbursed: float}})
    district_breakdown_json = Column(JSON, nullable=True)

    # Scheme-wise application count (JSON: {scheme_name: int})
    scheme_application_counts_json = Column(JSON, nullable=True)

    # Time-series data (JSON: [{date: str, applications: int, disbursed: float}, ...])
    monthly_trend_json = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    refreshed_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DisbursementSimulationRun(Base):
    """
    Immutable audit record for each DBT-style disbursement simulation.
    Real data is NEVER mutated by a simulation.
    """
    __tablename__ = "disbursement_simulation_run"

    id = Column(String(36), primary_key=True, default=_uuid)
    run_id = Column(String(20), nullable=False, unique=True)  # e.g. SIM-20240915-001

    # Parameters
    simulation_label = Column(String(200), nullable=False)
    scheme_filter = Column(String(100), nullable=True)    # None = all schemes
    income_band_filter = Column(String(50), nullable=True)
    ration_card_filter = Column(String(50), nullable=True)
    benefit_amount_inr = Column(Float, nullable=False)     # per-household amount
    simulation_date = Column(Date, nullable=False)         # effective date for eligibility check

    # Results
    eligible_family_count = Column(Integer, default=0)
    total_projected_disbursement_inr = Column(Float, default=0.0)
    district_breakdown_json = Column(JSON, nullable=True)  # {district: {count, amount}}
    scheme_breakdown_json = Column(JSON, nullable=True)    # {scheme: {count, amount}}
    notes = Column(Text, nullable=True)

    # Metadata
    triggered_by_user_id = Column(String(36), nullable=True)
    status = Column(String(30), default="COMPLETED")       # COMPLETED | FAILED
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
