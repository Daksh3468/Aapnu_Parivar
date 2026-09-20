import pytest
from datetime import datetime, date
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models.family import Family
from app.models.person import Person
from app.models.membership import FamilyMembership
from app.models.address import Address
from app.models.scheme import Scheme, SchemeCategory
from app.models.document import Document
from app.models.eligibility import SchemeEligibilityRecord
from app.models.enums import (
    FamilyStatusEnum,
    RationCardTypeEnum,
    IncomeBandEnum,
    HouseTypeEnum,
    OccupationTypeEnum,
    RegisteredByEnum,
    GenderEnum,
    MaritalStatusEnum,
    SocialCategoryEnum,
    EducationLevelEnum,
    VerificationStatusEnum,
    RoleInFamilyEnum,
    RelationToHeadEnum,
    MembershipReasonEnum,
    DocumentTypeEnum,
    DocumentStatusEnum,
    EligibilityStatusEnum,
    UserRoleEnum,
    JurisdictionScopeEnum,
)
from app.models.scheme import (
    SchemeLevelEnum,
    BenefitTypeEnum,
    EligibilityUnitEnum,
)
from app.models.user import UserAccount, OfficerJurisdiction
from app.core.security import create_access_token
from app.core.db import SessionLocal
from app.services.sync_service import sync_all_schemes_and_categories

client = TestClient(app)


@pytest.fixture
def eligibility_setup_data():
    db_session = SessionLocal()
    try:
        # 1. Sync Schemes
        sync_all_schemes_and_categories(db_session)
        s1 = db_session.query(Scheme).filter(Scheme.code == "PMKISAN").first()
        s2 = db_session.query(Scheme).filter(Scheme.code == "NAMO_SHREE").first()

        # 2. Create Address & Family
        addr = db_session.query(Address).filter(Address.line1 == "Sector 10 E-Block").first()
        if not addr:
            addr = Address(
                line1="Sector 10 E-Block",
                village_or_town="Gandhinagar",
                taluka="Gandhinagar",
                district_code=7, # Gandhinagar
                pincode="382010",
            )
            db_session.add(addr)
            db_session.commit()

        fam_id = "GJ-07-26-0000099-3"
        fam = db_session.query(Family).filter(Family.family_id == fam_id).first()
        p1 = db_session.query(Person).filter(Person.aadhaar_hash == "hashhead99").first()
        p2 = db_session.query(Person).filter(Person.aadhaar_hash == "hashgirl99").first()

        if not fam:
            fam = Family(
                family_id=fam_id,
                status=FamilyStatusEnum.VERIFIED,
                address_id=addr.address_id,
                ration_card_number="100020003099",
                ration_card_type=RationCardTypeEnum.PHH,
                annual_income_amount=150000.0,
                income_band=IncomeBandEnum.BAND_1L_2_5L,
                land_holding_acres=2.5,
                primary_occupation=OccupationTypeEnum.FARMER,
                registered_by=RegisteredByEnum.SELF,
            )
            db_session.add(fam)
            db_session.commit()

            # 3. Create Head Person & Female Student Member
            if not p1:
                p1 = Person(
                    aadhaar_hash="hashhead99",
                    aadhaar_last4="9001",
                    first_name="Ramesh",
                    last_name="Patel",
                    date_of_birth=date(1980, 1, 1),
                    gender=GenderEnum.MALE,
                    social_category=SocialCategoryEnum.SEBC,
                    verification_status=VerificationStatusEnum.VERIFIED,
                )
                db_session.add(p1)
            if not p2:
                p2 = Person(
                    aadhaar_hash="hashgirl99",
                    aadhaar_last4="9002",
                    first_name="Priya",
                    last_name="Patel",
                    date_of_birth=date(2010, 5, 15), # 16 years old female student
                    gender=GenderEnum.FEMALE,
                    social_category=SocialCategoryEnum.SEBC,
                    verification_status=VerificationStatusEnum.VERIFIED,
                )
                db_session.add(p2)

            db_session.commit()

            m1 = FamilyMembership(
                family_id=fam.family_id,
                person_id=p1.person_id,
                role_in_family=RoleInFamilyEnum.HEAD,
                relation_to_head=RelationToHeadEnum.SELF,
                membership_reason=MembershipReasonEnum.REGISTRATION,
            )
            m2 = FamilyMembership(
                family_id=fam.family_id,
                person_id=p2.person_id,
                role_in_family=RoleInFamilyEnum.DEPENDENT,
                relation_to_head=RelationToHeadEnum.DAUGHTER,
                membership_reason=MembershipReasonEnum.REGISTRATION,
            )
            db_session.add_all([m1, m2])
            db_session.commit()

        u = db_session.query(UserAccount).filter(UserAccount.login_id == "9999911199").first()
        if not u:
            u = UserAccount(
                login_id="9999911199",
                role=UserRoleEnum.CITIZEN_HEAD,
                password_hash="dummy_hash",
                person_id=p1.person_id if p1 else None,
            )
            db_session.add(u)
            db_session.commit()

        yield {
            "family": fam,
            "person_head": p1,
            "person_daughter": p2,
            "scheme_kisan": s1,
            "scheme_namo": s2,
            "user": u,
        }
    finally:
        db_session.close()


def test_eligibility_evaluation_and_document_flow(eligibility_setup_data):
    data = eligibility_setup_data
    fam_id = data["family"].family_id
    token = create_access_token(subject=data["user"].login_id, role=data["user"].role.value, user_id=str(data["user"].user_id))
    headers = {"Authorization": f"Bearer {token}"}

    # Clear any previous officer overrides for clean evaluation test
    db = SessionLocal()
    try:
        db.query(SchemeEligibilityRecord).filter(SchemeEligibilityRecord.family_id == fam_id).delete()
        db.commit()
    finally:
        db.close()

    # 1. Fetch Eligibility
    res = client.get(f"/api/v1/families/{fam_id}/eligibility", headers=headers)
    assert res.status_code == 200
    elig_list = res.json()
    assert len(elig_list) >= 18

    pmkisan = next(e for e in elig_list if e["scheme_code"] == "PMKISAN")
    assert pmkisan["status"] == EligibilityStatusEnum.AUTO_ELIGIBLE.value

    # 2. Upload Verified Document
    doc_res1 = client.post(
        f"/api/v1/families/{fam_id}/documents",
        json={
            "document_type": "LAND_RECORD",
            "document_number": "GJ-VERIFIED-LAND-101",
            "issuing_authority": "Revenue Dept, Gandhinagar",
        },
        headers=headers,
    )
    assert doc_res1.status_code == 201
    assert doc_res1.json()["status"] == DocumentStatusEnum.VERIFIED.value

    # 3. List uploaded documents
    docs_res = client.get(f"/api/v1/families/{fam_id}/documents", headers=headers)
    assert docs_res.status_code == 200
    assert len(docs_res.json()) >= 1


def test_officer_eligibility_review(eligibility_setup_data):
    data = eligibility_setup_data
    fam_id = data["family"].family_id

    db = SessionLocal()
    try:
        # Create Officer User
        off = db.query(UserAccount).filter(UserAccount.login_id == "officer_dist_07_elig").first()
        if not off:
            off = UserAccount(
                login_id="officer_dist_07_elig",
                password_hash="dummy_hash",
                role=UserRoleEnum.DISTRICT_OFFICER,
            )
            db.add(off)
            db.commit()
        if not off.jurisdictions:
            db.add(OfficerJurisdiction(user_id=off.user_id, scope_type=JurisdictionScopeEnum.DISTRICT, district_code=7))
            db.commit()

        token = create_access_token(subject=off.login_id, role=off.role.value, user_id=str(off.user_id))
        headers = {"Authorization": f"Bearer {token}"}

        scheme_id = data["scheme_kisan"].scheme_id

        # Officer overrides eligibility to OFFICER_APPROVED
        res = client.post(
            f"/api/v1/families/{fam_id}/eligibility/{scheme_id}/review",
            json={
                "status": "OFFICER_APPROVED",
                "officer_notes": "Special relaxation granted under district quota by Officer 07",
            },
            headers=headers,
        )
        assert res.status_code == 200
        res_data = res.json()
        assert res_data["status"] == "OFFICER_APPROVED"
        assert res_data["officer_notes"] == "Special relaxation granted under district quota by Officer 07"
    finally:
        db.close()
