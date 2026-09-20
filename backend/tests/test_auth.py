import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import hash_password, verify_password, create_access_token, decode_token
from app.core.db import SessionLocal
from app.models.user import UserAccount, OfficerJurisdiction
from app.models.enums import UserRoleEnum, JurisdictionScopeEnum
from app.services.otp_service import create_otp_challenge, verify_otp_challenge
from app.core.jurisdiction import build_officer_jurisdiction_scope, apply_family_jurisdiction_filter
from app.models.family import Family
from app.models.address import Address

client = TestClient(app)


def test_password_hashing():
    pwd = "SecretPassword123"
    hashed = hash_password(pwd)
    assert verify_password(pwd, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_jwt_token_generation_and_decode():
    token = create_access_token(subject="admin@gujarat.gov.in", role="STATE_ADMIN", user_id="user-123")
    payload = decode_token(token)
    assert payload is not None
    assert payload["sub"] == "admin@gujarat.gov.in"
    assert payload["role"] == "STATE_ADMIN"
    assert payload["user_id"] == "user-123"


def test_otp_challenge_lifecycle():
    db = SessionLocal()
    try:
        mobile = "9999988888"
        challenge, raw_code = create_otp_challenge(db, target_mobile=mobile, purpose="LOGIN")
        assert len(raw_code) == 6
        assert raw_code.isdigit()

        # Incorrect OTP test
        success, msg = verify_otp_challenge(db, target_mobile=mobile, purpose="LOGIN", submitted_code="000000")
        assert success is False

        # Correct OTP test
        success, msg = verify_otp_challenge(db, target_mobile=mobile, purpose="LOGIN", submitted_code=raw_code)
        assert success is True
    finally:
        db.close()


def test_login_api_with_password():
    response = client.post(
        "/api/v1/auth/login",
        json={"login_id": "admin@gujarat.gov.in", "password": "Admin@123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["role"] == "STATE_ADMIN"


def test_otp_request_and_login_api():
    # 1. Request OTP
    res1 = client.post("/api/v1/auth/otp/request", json={"mobile": "9876543210", "purpose": "LOGIN"})
    assert res1.status_code == 200
    demo_otp = res1.json().get("demo_otp")
    assert demo_otp is not None

    # 2. Login with OTP
    res2 = client.post("/api/v1/auth/login", json={"login_id": "9876543210", "otp_code": demo_otp})
    assert res2.status_code == 200
    data = res2.json()
    assert "access_token" in data


def test_failed_otp_login():
    res = client.post("/api/v1/auth/login", json={"login_id": "9876543210", "otp_code": "000000"})
    assert res.status_code == 401
    assert "detail" in res.json()



def test_get_me_protected_endpoint():
    # Login first
    login_res = client.post(
        "/api/v1/auth/login",
        json={"login_id": "admin@gujarat.gov.in", "password": "Admin@123"},
    )
    token = login_res.json()["access_token"]

    # Call /auth/me with Bearer token
    res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()
    assert data["login_id"] == "admin@gujarat.gov.in"
    assert data["role"] == "STATE_ADMIN"


def test_jurisdiction_scoping_isolation():
    db = SessionLocal()
    try:
        # User 1: District 7 Officer
        user_d7 = db.query(UserAccount).filter(UserAccount.login_id == "district07@gujarat.gov.in").first()
        scope_d7 = build_officer_jurisdiction_scope(user_d7)

        assert scope_d7.is_statewide is False
        assert 7 in scope_d7.district_codes

        # Query Family filtered by jurisdiction scope
        query = db.query(Family)
        filtered_q = apply_family_jurisdiction_filter(query, scope_d7)

        # Assert query builds SQL statement containing district_code filter
        sql_str = str(filtered_q.statement)
        assert "address.district_code" in sql_str
    finally:
        db.close()


def test_authenticated_password_change_flow():
    # 1. Login as admin
    login_res = client.post(
        "/api/v1/auth/login",
        json={"login_id": "admin@gujarat.gov.in", "password": "Admin@123"},
    )
    token = login_res.json()["access_token"]

    # 2. Change password with wrong current password -> 400
    fail_res = client.post(
        "/api/v1/auth/password/change",
        headers={"Authorization": f"Bearer {token}"},
        json={"current_password": "WrongPassword", "new_password": "NewSecretPass@123"},
    )
    assert fail_res.status_code == 400

    # 3. Change password successfully
    succ_res = client.post(
        "/api/v1/auth/password/change",
        headers={"Authorization": f"Bearer {token}"},
        json={"current_password": "Admin@123", "new_password": "NewSecretPass@123"},
    )
    assert succ_res.status_code == 200
    assert "Password changed successfully" in succ_res.json()["message"]

    # 4. Re-verify login with new password
    new_login = client.post(
        "/api/v1/auth/login",
        json={"login_id": "admin@gujarat.gov.in", "password": "NewSecretPass@123"},
    )
    assert new_login.status_code == 200

    # 5. Restore original password for other tests
    client.post(
        "/api/v1/auth/password/change",
        headers={"Authorization": f"Bearer {new_login.json()['access_token']}"},
        json={"current_password": "NewSecretPass@123", "new_password": "Admin@123"},
    )
