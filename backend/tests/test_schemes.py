import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.db import SessionLocal
from app.services.sync_service import sync_all_schemes_and_categories
from app.models.scheme import Scheme, SchemeCategory

client = TestClient(app)


def test_scheme_synchronization_service():
    db = SessionLocal()
    try:
        count = sync_all_schemes_and_categories(db)
        assert count >= 18

        cat_count = db.query(SchemeCategory).count()
        assert cat_count >= 8

        scheme_count = db.query(Scheme).count()
        assert scheme_count >= 18
    finally:
        db.close()


def test_categories_api():
    res = client.get("/api/v1/schemes/categories")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 8
    assert any(c["name"] == "Agriculture & Farmers" for c in data)


def test_schemes_catalog_filters_and_search():
    # 1. Get all schemes
    res = client.get("/api/v1/schemes")
    assert res.status_code == 200
    all_schemes = res.json()
    assert len(all_schemes) >= 18

    # 2. Filter by Level = CENTRAL
    res_central = client.get("/api/v1/schemes?level=CENTRAL")
    assert res_central.status_code == 200
    central_schemes = res_central.json()
    assert all(s["level"] == "CENTRAL" for s in central_schemes)

    # 3. Filter by Level = STATE
    res_state = client.get("/api/v1/schemes?level=STATE")
    assert res_state.status_code == 200
    state_schemes = res_state.json()
    assert all(s["level"] == "STATE" for s in state_schemes)

    # 4. Search query
    res_search = client.get("/api/v1/schemes?search=Kisan")
    assert res_search.status_code == 200
    search_results = res_search.json()
    assert len(search_results) >= 2


def test_get_scheme_by_code():
    res = client.get("/api/v1/schemes/PMKISAN")
    assert res.status_code == 200
    data = res.json()
    assert data["code"] == "PMKISAN"
    assert data["level"] == "CENTRAL"
    assert "PM-KISAN" in data["name"]


def test_connector_sync_and_health():
    res = client.post("/api/v1/connectors/sync")
    assert res.status_code == 200
    assert "synced_count" in res.json()

    h_res = client.get("/api/v1/connectors/health")
    assert h_res.status_code == 200
    health_list = h_res.json()
    assert len(health_list) >= 2
