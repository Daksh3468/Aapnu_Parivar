"""
test_analytics.py
=================
Tests for the State Analytics Dashboard and Disbursement Simulation APIs.

Covers:
  - Snapshot refresh + data integrity
  - Overview endpoint availability (no auth needed)
  - Force-refresh requires officer+ role
  - Simulation endpoint: DISTRICT_OFFICER can run, CITIZEN cannot
  - Simulation result persisted and retrievable
  - Simulation engine handles empty result-set gracefully
"""
import pytest
from fastapi.testclient import TestClient

from app.core.db import SessionLocal
from app.main import app
from app.services.analytics_service import (
    refresh_daily_snapshot,
    run_disbursement_simulation,
    list_simulation_runs,
)

client = TestClient(app)

API = "/api/v1"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _officer_token() -> str:
    """Log in as STATE_ADMIN (seeded in fixtures)."""
    res = client.post(f"{API}/auth/login", json={"login_id": "admin@gujarat.gov.in", "password": "Admin@123"})
    assert res.status_code == 200, res.text
    return res.json()["access_token"]


def _citizen_token() -> str:
    """Log in as a citizen via OTP (seeded mobile)."""
    res1 = client.post(f"{API}/auth/otp/request", json={"mobile": "9876543210", "purpose": "LOGIN"})
    assert res1.status_code == 200
    otp = res1.json()["demo_otp"]
    res2 = client.post(f"{API}/auth/login", json={"login_id": "9876543210", "otp_code": otp})
    assert res2.status_code == 200
    return res2.json()["access_token"]


# ---------------------------------------------------------------------------
# Unit-level service tests (hit SQLite in-memory via SessionLocal)
# ---------------------------------------------------------------------------

class TestAnalyticsService:
    def test_refresh_snapshot_returns_model(self):
        db = SessionLocal()
        try:
            snap = refresh_daily_snapshot(db)
            assert snap is not None
            assert snap.total_families >= 0
            assert snap.total_scheme_applications >= 0
            assert isinstance(snap.district_breakdown_json, (dict, type(None)))
        finally:
            db.close()

    def test_snapshot_idempotent_on_same_day(self):
        """Calling refresh twice on the same day should upsert, not duplicate."""
        db = SessionLocal()
        try:
            s1 = refresh_daily_snapshot(db)
            s2 = refresh_daily_snapshot(db)
            assert s1.id == s2.id  # same row
        finally:
            db.close()

    def test_simulation_produces_result(self):
        db = SessionLocal()
        try:
            run = run_disbursement_simulation(
                db,
                simulation_label="Test simulation",
                benefit_amount_inr=5000.0,
            )
            assert run is not None
            assert run.status == "COMPLETED"
            assert run.eligible_family_count >= 0
            assert run.total_projected_disbursement_inr == run.eligible_family_count * 5000.0
            assert run.run_id.startswith("SIM-")
        finally:
            db.close()

    def test_simulation_with_income_filter(self):
        db = SessionLocal()
        try:
            run_all = run_disbursement_simulation(db, simulation_label="All families", benefit_amount_inr=1000.0)
            run_filtered = run_disbursement_simulation(
                db,
                simulation_label="BPL only",
                benefit_amount_inr=1000.0,
                ration_card_filter="AAY",
            )
            # Filtered result should be <= full result
            assert run_filtered.eligible_family_count <= run_all.eligible_family_count
        finally:
            db.close()

    def test_list_simulation_runs(self):
        db = SessionLocal()
        try:
            # Ensure at least one run exists
            run_disbursement_simulation(db, simulation_label="List test", benefit_amount_inr=500.0)
            runs = list_simulation_runs(db, limit=5)
            assert isinstance(runs, list)
            assert len(runs) >= 1
        finally:
            db.close()


# ---------------------------------------------------------------------------
# API-level tests
# ---------------------------------------------------------------------------

class TestAnalyticsAPI:
    def test_overview_returns_200_no_auth(self):
        """The overview endpoint should be accessible without authentication."""
        res = client.get(f"{API}/analytics/overview")
        assert res.status_code == 200
        data = res.json()
        assert "total_families" in data
        assert "total_disbursed_amount_inr" in data
        assert "monthly_trend" in data
        assert isinstance(data["district_breakdown"], dict)

    def test_force_refresh_requires_auth(self):
        res = client.post(f"{API}/analytics/refresh")
        assert res.status_code == 401

    def test_force_refresh_as_officer(self):
        token = _officer_token()
        res = client.post(f"{API}/analytics/refresh", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
        data = res.json()
        assert "snapshot_date" in data

    def test_simulate_requires_auth(self):
        res = client.post(f"{API}/analytics/simulate", json={
            "simulation_label": "Unauthorized",
            "benefit_amount_inr": 1000.0,
        })
        assert res.status_code == 401

    def test_simulate_citizen_forbidden(self):
        token = _citizen_token()
        res = client.post(f"{API}/analytics/simulate", json={
            "simulation_label": "Citizen sim",
            "benefit_amount_inr": 1000.0,
        }, headers={"Authorization": f"Bearer {token}"})
        # Citizens cannot run simulations
        assert res.status_code == 403

    def test_simulate_as_state_admin(self):
        token = _officer_token()
        res = client.post(f"{API}/analytics/simulate", json={
            "simulation_label": "Gujarat Q4 2025 Projection",
            "benefit_amount_inr": 6000.0,
            "ration_card_filter": "PHH",
        }, headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "COMPLETED"
        assert "eligible_family_count" in data
        assert "total_projected_disbursement_inr" in data
        assert data["total_projected_disbursement_inr"] == data["eligible_family_count"] * 6000.0
        assert data["run_id"].startswith("SIM-")

    def test_list_simulations_as_officer(self):
        token = _officer_token()
        # Create a run first
        client.post(f"{API}/analytics/simulate", json={
            "simulation_label": "List test",
            "benefit_amount_inr": 500.0,
        }, headers={"Authorization": f"Bearer {token}"})

        res = client.get(f"{API}/analytics/simulations", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
        data = res.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert "run_id" in data[0]

    def test_get_simulation_by_run_id(self):
        token = _officer_token()
        # Create a run
        sim_res = client.post(f"{API}/analytics/simulate", json={
            "simulation_label": "Fetch by ID test",
            "benefit_amount_inr": 2500.0,
        }, headers={"Authorization": f"Bearer {token}"})
        assert sim_res.status_code == 200
        run_id = sim_res.json()["run_id"]

        # Fetch it
        fetch_res = client.get(f"{API}/analytics/simulations/{run_id}", headers={"Authorization": f"Bearer {token}"})
        assert fetch_res.status_code == 200
        assert fetch_res.json()["run_id"] == run_id

    def test_get_simulation_404_for_unknown(self):
        token = _officer_token()
        res = client.get(f"{API}/analytics/simulations/SIM-DOES-NOT-EXIST", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 404

    def test_overview_data_types(self):
        """Ensure numeric fields are not null/None in the response."""
        res = client.get(f"{API}/analytics/overview")
        assert res.status_code == 200
        data = res.json()
        for int_field in [
            "total_families", "active_families", "total_members",
            "total_scheme_applications", "approved_applications",
        ]:
            assert isinstance(data[int_field], int), f"{int_field} should be int"
        assert isinstance(data["total_disbursed_amount_inr"], float)
