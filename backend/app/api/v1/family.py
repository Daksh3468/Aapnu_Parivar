from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.auth_deps import get_current_user, get_active_citizen_membership, require_roles
from app.models.user import UserAccount
from app.models.enums import UserRoleEnum, RegisteredByEnum, RoleInFamilyEnum
from app.models.district import District
from app.models.family import Family
from app.models.membership import FamilyMembership
from app.schemas.family import (
    FamilyRegisterPayload,
    FamilyResponseSchema,
    AddressResponseSchema,
    MemberResponseSchema,
)
from app.services.family_service import register_new_family, get_family_details
from app.utils.family_id import is_valid_family_id
from app.utils.masking import mask_mobile, mask_aadhaar_last4

router = APIRouter()


def _build_family_response(db: Session, family: Family) -> FamilyResponseSchema:
    """Helper to convert Family ORM object to API response schema."""
    district = db.query(District).filter(District.district_code == family.address.district_code).first()
    district_name = district.name if district else f"District {family.address.district_code}"

    address_dto = AddressResponseSchema(
        address_id=family.address.address_id,
        line1=family.address.line1,
        village_or_town=family.address.village_or_town,
        taluka=family.address.taluka,
        district_code=family.address.district_code,
        district_name=district_name,
        pincode=family.address.pincode,
    )

    members_dto = []
    head_name = "Unknown"

    for m in family.memberships:
        if m.end_date is None:  # Active members
            if m.role_in_family == RoleInFamilyEnum.HEAD:
                head_name = m.person.full_name

            members_dto.append(
                MemberResponseSchema(
                    person_id=m.person.person_id,
                    full_name=m.person.full_name,
                    dob=m.person.dob,
                    gender=m.person.gender.value,
                    marital_status=m.person.marital_status.value,
                    mobile_masked=mask_mobile(m.person.mobile) if m.person.mobile else None,
                    relation_to_head=m.relation_to_head.value,
                    role_in_family=m.role_in_family.value,
                    verification_status=m.person.verification_status.value,
                    aadhaar_last4=mask_aadhaar_last4(m.person.aadhaar_last4) if m.person.aadhaar_last4 else None,
                )
            )

    return FamilyResponseSchema(
        family_id=family.family_id,
        status=family.status.value,
        registered_by=family.registered_by.value,
        created_at=family.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        address=address_dto,
        head_name=head_name,
        ration_card_type=family.ration_card_type.value,
        income_band=family.income_band.value,
        member_count=len(members_dto),
        members=members_dto,
    )


@router.post("/families", response_model=FamilyResponseSchema, status_code=status.HTTP_201_CREATED)
def create_family(
    payload: FamilyRegisterPayload,
    db: Session = Depends(get_db),
):
    """
    Register a new family household.
    Issues a structured 12-digit Verhoeff Family ID (GJ-DD-YY-SSSSSSS-C).
    """
    family = register_new_family(db=db, payload=payload, registered_by=RegisteredByEnum.SELF)
    return _build_family_response(db, family)


@router.get("/families/me", response_model=FamilyResponseSchema)
def get_my_family(
    current_user: UserAccount = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get authenticated citizen's active household profile."""
    membership = get_active_citizen_membership(current_user, db)
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active family membership found for current citizen account.",
        )

    family = get_family_details(db, membership.family_id)
    if not family:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Family profile not found.")

    return _build_family_response(db, family)


@router.get("/families/{family_id}", response_model=FamilyResponseSchema)
def get_family_by_id(
    family_id: str,
    db: Session = Depends(get_db),
):
    """Retrieve family details by Family ID."""
    clean_id = family_id.strip().upper()
    family = get_family_details(db, clean_id)
    if not family:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Family ID '{clean_id}' not found in registry.",
        )

    return _build_family_response(db, family)


@router.get("/lookup/family/{family_id}")
def lookup_family_existence(family_id: str, db: Session = Depends(get_db)):
    """Lookup Family ID existence and check-digit validity."""
    clean_id = family_id.strip().upper()
    is_valid = is_valid_family_id(clean_id)

    family = db.query(Family).filter(Family.family_id == clean_id).first()
    exists = family is not None

    return {
        "family_id": clean_id,
        "is_valid_format": is_valid,
        "exists": exists,
        "status": family.status.value if family else None,
    }
