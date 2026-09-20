import pytest
from datetime import date
from fastapi.testclient import TestClient
from app.main import app
from app.core.db import SessionLocal
from app.models.person import Person
from app.models.enums import GenderEnum, VerificationStatusEnum
from app.utils.aadhaar import generate_synthetic_aadhaar, hash_aadhaar
from app.services.duplicate_service import run_duplicate_check_for_person

client = TestClient(app)


def test_aadhaar_verification_api_flow():
    db = SessionLocal()
    try:
        # Create person
        p = Person(full_name="Bhaveshbhai Patel", dob=date(1982, 6, 15), gender=GenderEnum.MALE)
        db.add(p)
        db.commit()

        syn_aadhaar = generate_synthetic_aadhaar()

        # Step 1: Start Verification
        res1 = client.post(
            f"/api/v1/members/{p.person_id}/verify/start",
            json={"aadhaar_number": syn_aadhaar},
        )
        assert res1.status_code == 200
        demo_otp = res1.json().get("demo_otp")
        assert demo_otp is not None

        # Step 2: Confirm Verification
        res2 = client.post(
            f"/api/v1/members/{p.person_id}/verify/confirm",
            json={"aadhaar_number": syn_aadhaar, "otp_code": demo_otp},
        )
        assert res2.status_code == 200
        data = res2.json()
        assert data["verification_status"] == "VERIFIED"
        assert data["aadhaar_last4_masked"] == f"XXXX-XXXX-{syn_aadhaar[-4:]}"

        # Step 3: Assert full Aadhaar is NEVER stored in database
        db.refresh(p)
        assert p.aadhaar_last4 == syn_aadhaar[-4:]
        assert p.aadhaar_hash == hash_aadhaar(syn_aadhaar)
        assert syn_aadhaar not in str(p.__dict__)
    finally:
        db.close()


def test_duplicate_aadhaar_hash_is_blocked():
    db = SessionLocal()
    try:
        syn_aadhaar = generate_synthetic_aadhaar()

        # Person 1 verified with syn_aadhaar
        p1 = Person(
            full_name="Original Person",
            dob=date(1990, 1, 1),
            gender=GenderEnum.MALE,
            aadhaar_last4=syn_aadhaar[-4:],
            aadhaar_hash=hash_aadhaar(syn_aadhaar),
            verification_status=VerificationStatusEnum.VERIFIED,
        )
        # Person 2 unverified
        p2 = Person(full_name="Impostor Person", dob=date(1990, 1, 1), gender=GenderEnum.MALE)
        db.add_all([p1, p2])
        db.commit()

        # Try to verify Person 2 with same Aadhaar number -> MUST BE BLOCKED
        res = client.post(
            f"/api/v1/members/{p2.person_id}/verify/start",
            json={"aadhaar_number": syn_aadhaar},
        )
        assert res.status_code == 409  # Conflict
    finally:
        db.close()


def test_fuzzy_duplicate_detection_scoring():
    db = SessionLocal()
    try:
        p1 = Person(
            full_name="Rajeshkumar Patel",
            dob=date(1985, 3, 10),
            gender=GenderEnum.MALE,
            mobile="9876599999",
        )
        p2 = Person(
            full_name="Rajesh Patel",
            dob=date(1985, 3, 10),
            gender=GenderEnum.MALE,
            mobile="9876599999",
        )
        db.add_all([p1, p2])
        db.commit()

        # Run duplicate check for Person 2 against Person 1
        blocked, message, flag = run_duplicate_check_for_person(db, p2)
        assert flag is not None
        assert flag.score >= 0.75
        assert flag.status == "OPEN"
    finally:
        db.close()
