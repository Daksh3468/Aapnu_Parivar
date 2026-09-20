import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.db import SessionLocal
from app.models.user import UserAccount
from app.models.family import Family
from app.models.person import Person
from app.models.membership import FamilyMembership
from app.models.enums import RoleInFamilyEnum, LifeEventTypeEnum, SplitStatusEnum, MembershipReasonEnum, RelationToHeadEnum


from app.models.life_event import LifeEventRecord, FamilySplitRecord
from app.services.life_event_service import LifeEventService

client = TestClient(app)


def test_life_event_registration_and_list():
    db = SessionLocal()
    try:
        # Get head user and family
        user = db.query(UserAccount).filter(UserAccount.login_id == "9876543210").first()
        fam = db.query(Family).first()
        assert fam is not None

        # Login
        login_res = client.post("/api/v1/auth/login", json={"login_id": "9876543210", "password": "Password@123"})
        if login_res.status_code != 200:
            # Request OTP fallback
            otp_res = client.post("/api/v1/auth/otp/request", json={"mobile": "9876543210", "purpose": "LOGIN"})
            demo_code = otp_res.json()["demo_otp"]
            login_res = client.post("/api/v1/auth/login", json={"login_id": "9876543210", "otp_code": demo_code})

        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Register Birth event
        reg_res = client.post(
            f"/api/v1/families/{fam.family_id}/life-events",
            headers=headers,
            json={
                "event_type": "BIRTH",
                "event_date": "2026-01-15",
                "description": "Birth of child registered in hospital",
            },
        )
        assert reg_res.status_code == 201
        data = reg_res.json()
        assert data["event_type"] == "BIRTH"

        # 2. List Life Events
        list_res = client.get(f"/api/v1/families/{fam.family_id}/life-events", headers=headers)
        assert list_res.status_code == 200
        events = list_res.json()
        assert len(events) >= 1
        assert any(e["event_type"] == "BIRTH" for e in events)
    finally:
        db.close()


def test_family_split_anomaly_scoring_and_execution():
    db = SessionLocal()
    try:
        # Find a family with >= 2 members or add a second person
        fam = db.query(Family).first()
        active_memberships = [m for m in fam.memberships if m.end_date is None]

        if len(active_memberships) < 2:
            import uuid
            from datetime import date
            p2 = Person(
                person_id=str(uuid.uuid4()),
                full_name="Ramesh Patel",
                dob=date(2000, 5, 15),
                gender="MALE",
                aadhaar_hash=str(uuid.uuid4()),
                aadhaar_last4="8812",
            )
            db.add(p2)
            db.flush()


            m2 = FamilyMembership(
                family_id=fam.family_id,
                person_id=p2.person_id,
                role_in_family=RoleInFamilyEnum.ADULT,
                relation_to_head=RelationToHeadEnum.SON,
                start_date=date(2026, 1, 1),
                start_reason=MembershipReasonEnum.REGISTRATION,
            )
            db.add(m2)
            db.commit()


            active_memberships = [m for m in fam.memberships if m.end_date is None]

        moved_pid = active_memberships[-1].person_id

        # Calculate anomaly score for simple split
        score, flags = LifeEventService.calculate_split_anomaly_score(
            db=db,
            source_family_id=fam.family_id,
            moved_person_ids=[moved_pid],
            split_reason="Marriage and setting up independent residence in city",
        )
        assert isinstance(score, float)


        # OTP Login for citizen
        otp_res = client.post("/api/v1/auth/otp/request", json={"mobile": "9876543210", "purpose": "LOGIN"})
        demo_code = otp_res.json()["demo_otp"]
        login_res = client.post("/api/v1/auth/login", json={"login_id": "9876543210", "otp_code": demo_code})
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}


        # Submit split request
        split_res = client.post(
            f"/api/v1/families/{fam.family_id}/split",
            headers=headers,
            json={
                "moved_person_ids": [moved_pid],
                "new_head_person_id": moved_pid,
                "split_reason": "Moving out to new residence after employment change",
            },
        )
        assert split_res.status_code == 200
        s_data = split_res.json()
        assert s_data["source_family_id"] == fam.family_id
        assert s_data["status"] in ["AUTOMATICALLY_APPROVED", "PENDING_OFFICER_REVIEW"]

        if s_data["status"] == "AUTOMATICALLY_APPROVED":
            assert s_data["new_family_id"] is not None
            assert s_data["new_family_id"].startswith("GJ-")
    finally:
        db.close()


def test_officer_split_queue_and_review():
    db = SessionLocal()
    try:
        # State Admin login
        adm_login = client.post("/api/v1/auth/login", json={"login_id": "admin@gujarat.gov.in", "password": "Admin@123"})
        assert adm_login.status_code == 200
        token = adm_login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Get officer splits queue
        q_res = client.get("/api/v1/officer/splits-queue", headers=headers)
        assert q_res.status_code == 200
        items = q_res.json()
        assert isinstance(items, list)
    finally:
        db.close()
