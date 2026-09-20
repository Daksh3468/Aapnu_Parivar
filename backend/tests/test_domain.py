import pytest
from datetime import date
from sqlalchemy.exc import IntegrityError
from app.core.db import SessionLocal, Base, engine
from app.models.district import District
from app.models.pincode import PincodeMaster
from app.models.address import Address
from app.models.person import Person
from app.models.family import Family
from app.models.membership import FamilyMembership
from app.models.enums import (
    GenderEnum,
    FamilyStatusEnum,
    RoleInFamilyEnum,
    RelationToHeadEnum,
    MembershipReasonEnum,
)
from app.utils.family_id import (
    verhoeff_check_digit,
    verhoeff_valid,
    new_family_id,
    is_valid_family_id,
)
from app.utils.masking import mask_mobile, mask_ration_card, mask_aadhaar_last4
from app.utils.aadhaar import hash_aadhaar, generate_synthetic_aadhaar, is_valid_aadhaar_format
from app.utils.normalize import normalize_name, normalize_address


# Verhoeff & Family ID Tests
def test_verhoeff_check_digit():
    assert verhoeff_check_digit("07264831927") == "1"
    assert verhoeff_valid("072648319271") is True


def test_verhoeff_detects_single_digit_errors():
    valid = "072648319271"
    # Single digit mutation
    mutated = "072648319281"
    assert verhoeff_valid(mutated) is False


def test_verhoeff_detects_transposition_errors():
    valid = "072648319271"
    # Adjacent transposition (92 -> 29)
    mutated = "072648312971"
    assert verhoeff_valid(mutated) is False


def test_family_id_generation_and_validation():
    fid = new_family_id(district_code=7, year=2026)
    assert fid.startswith("GJ-07-26-")
    assert is_valid_family_id(fid) is True
    # Test unformatted string without hyphens
    clean_fid = fid.replace("-", "")
    assert is_valid_family_id(clean_fid) is True


# Masking & Hashing Tests
def test_masking_utilities():
    assert mask_mobile("9876543210") == "98XXXXXX10"
    assert mask_ration_card("GJ1234567890") == "GJXXXXXX7890"
    assert mask_aadhaar_last4("1234") == "XXXX-XXXX-1234"


def test_aadhaar_hashing_and_synthetic():
    h1 = hash_aadhaar("123456789012")
    h2 = hash_aadhaar("123456789012")
    assert h1 == h2
    assert len(h1) == 64

    syn = generate_synthetic_aadhaar()
    assert syn.startswith("1")
    assert len(syn) == 12
    assert is_valid_aadhaar_format(syn) is True


def test_normalization():
    assert normalize_name("Shri Rajeshkumar Patel") == "rajeshkumar"
    assert normalize_address("123, Ring Road, Sector-11!") == "123 ring road sector 11"


# Database Invariant Constraints Tests
def test_one_active_membership_per_person_constraint():
    db = SessionLocal()
    try:
        # Create person
        p = Person(full_name="Test Person", dob=date(1990, 1, 1), gender=GenderEnum.MALE)
        db.add(p)
        db.commit()

        # Create two families with unique Family IDs
        fid1 = new_family_id(1, 26)
        fid2 = new_family_id(1, 26)
        f1 = Family(family_id=fid1, address_id="dummy-addr-1", status=FamilyStatusEnum.SUBMITTED)
        f2 = Family(family_id=fid2, address_id="dummy-addr-2", status=FamilyStatusEnum.SUBMITTED)
        db.add_all([f1, f2])
        db.commit()

        # Add 1st active membership
        m1 = FamilyMembership(
            person_id=p.person_id,
            family_id=f1.family_id,
            role_in_family=RoleInFamilyEnum.HEAD,
            relation_to_head=RelationToHeadEnum.SELF,
            start_date=date(2026, 1, 1),
            end_date=None,  # Active
        )
        db.add(m1)
        db.commit()

        # Try to add 2nd active membership for same person -> MUST FAIL
        m2 = FamilyMembership(
            person_id=p.person_id,
            family_id=f2.family_id,
            role_in_family=RoleInFamilyEnum.ADULT,
            relation_to_head=RelationToHeadEnum.OTHER,
            start_date=date(2026, 1, 1),
            end_date=None,  # Active
        )
        db.add(m2)
        with pytest.raises(IntegrityError):
            db.commit()
    finally:
        db.rollback()
        db.close()


def test_one_active_head_per_family_constraint():
    db = SessionLocal()
    try:
        # Create 2 persons
        p1 = Person(full_name="Person 1", dob=date(1985, 1, 1), gender=GenderEnum.MALE)
        p2 = Person(full_name="Person 2", dob=date(1988, 1, 1), gender=GenderEnum.FEMALE)
        db.add_all([p1, p2])
        db.commit()

        # Create family
        fid = new_family_id(1, 26)
        f = Family(family_id=fid, address_id="dummy-addr-3", status=FamilyStatusEnum.SUBMITTED)
        db.add(f)
        db.commit()

        # Add 1st active head
        m1 = FamilyMembership(
            person_id=p1.person_id,
            family_id=f.family_id,
            role_in_family=RoleInFamilyEnum.HEAD,
            relation_to_head=RelationToHeadEnum.SELF,
            start_date=date(2026, 1, 1),
            end_date=None,  # Active Head
        )
        db.add(m1)
        db.commit()

        # Try to add 2nd active head for same family -> MUST FAIL
        m2 = FamilyMembership(
            person_id=p2.person_id,
            family_id=f.family_id,
            role_in_family=RoleInFamilyEnum.HEAD,
            relation_to_head=RelationToHeadEnum.SPOUSE,
            start_date=date(2026, 1, 1),
            end_date=None,  # Active Head
        )
        db.add(m2)
        with pytest.raises(IntegrityError):
            db.commit()
    finally:
        db.rollback()
        db.close()
