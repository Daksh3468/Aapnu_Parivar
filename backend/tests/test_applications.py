from datetime import date
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.core.db import SessionLocal
from app.core.security import create_access_token
from app.models.address import Address
from app.models.enums import GenderEnum, RoleInFamilyEnum, SocialCategoryEnum, UserRoleEnum
from app.models.family import Family
from app.models.membership import FamilyMembership
from app.models.person import Person
from app.models.scheme import Scheme
from app.models.user import UserAccount
from app.services.sync_service import sync_all_schemes_and_categories

client = TestClient(app)


def test_application_submit_duplicate_block_and_status_refresh():
    db = SessionLocal()
    try:
        sync_all_schemes_and_categories(db)
        scheme = db.query(Scheme).filter(Scheme.code == "PMKISAN").first()
        assert scheme is not None

        suffix = uuid4().hex[:8]
        address = Address(line1=f"Phase 8 Test Lane {suffix}", village_or_town="Gandhinagar", taluka="Gandhinagar", district_code=7, pincode="382010")
        db.add(address)
        db.commit()
        family = Family(family_id=f"GJ-07-26-{suffix}-6", address_id=address.address_id, annual_income_amount=100000, land_holding_acres=1)
        person = Person(full_name="Phase Eight Head", dob=date(1975, 1, 1), gender=GenderEnum.MALE, social_category=SocialCategoryEnum.GENERAL)
        db.add_all([family, person])
        db.commit()
        db.add(FamilyMembership(person_id=person.person_id, family_id=family.family_id, role_in_family=RoleInFamilyEnum.HEAD))
        user = UserAccount(login_id=f"phase8-{suffix}@example.test", password_hash="not-used", person_id=person.person_id, role=UserRoleEnum.CITIZEN_HEAD)
        db.add(user)
        db.commit()

        token = create_access_token(user.login_id, user.role.value, user.user_id, person_id=person.person_id, family_id=family.family_id)
        headers = {"Authorization": f"Bearer {token}"}
        response = client.post(f"/api/v1/families/{family.family_id}/applications", json={"scheme_id": scheme.scheme_id}, headers=headers)
        assert response.status_code == 201
        submitted = response.json()
        assert submitted["status"] == "SUBMITTED"
        assert submitted["external_reference"].startswith(("DG-", "JS-"))
        assert len(submitted["history"]) == 1

        duplicate = client.post(f"/api/v1/families/{family.family_id}/applications", json={"scheme_id": scheme.scheme_id}, headers=headers)
        assert duplicate.status_code == 409

        refreshed = client.post(f"/api/v1/families/{family.family_id}/applications/{submitted['application_id']}/refresh", headers=headers)
        assert refreshed.status_code == 200
        assert refreshed.json()["status"] in {"UNDER_REVIEW", "APPROVED"}
        assert len(refreshed.json()["history"]) == 2
    finally:
        db.close()
