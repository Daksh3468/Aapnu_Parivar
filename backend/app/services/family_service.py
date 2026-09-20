from datetime import date, datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.address import Address
from app.models.family import Family
from app.models.person import Person
from app.models.membership import FamilyMembership
from app.models.district import District
from app.models.user import UserAccount
from app.models.audit import ConsentRecord
from app.models.enums import (
    FamilyStatusEnum,
    RoleInFamilyEnum,
    RegisteredByEnum,
    VerificationStatusEnum,
    UserRoleEnum,
    UserAccountStatusEnum,
)
from app.schemas.family import FamilyRegisterPayload, MemberCreateSchema
from app.utils.family_id import new_family_id
from app.utils.masking import mask_mobile, mask_aadhaar_last4
from app.core.security import hash_password
from app.services.audit_service import write_audit
from app.services.duplicate_service import run_duplicate_check_for_person


def register_new_family(
    db: Session,
    payload: FamilyRegisterPayload,
    registered_by: RegisteredByEnum = RegisteredByEnum.SELF,
    registered_by_user: Optional[UserAccount] = None,
) -> Family:
    """
    Register a new family in the system:
    1. Creates Address record
    2. Issues a unique 12-digit Verhoeff Family ID (GJ-DD-YY-SSSSSSS-C)
    3. Creates Person & FamilyMembership rows for Head and Members
    4. Records mandatory Citizen Consents
    5. Writes append-only Audit Log
    6. If registered by Officer, creates PENDING_CLAIM citizen user accounts
    """
    # 1. Create Address
    address = Address(
        line1=payload.address.line1,
        village_or_town=payload.address.village_or_town,
        taluka=payload.address.taluka,
        district_code=payload.address.district_code,
        pincode=payload.address.pincode,
    )
    db.add(address)
    db.commit()
    db.refresh(address)

    # 2. Issue Family ID
    current_year = date.today().year
    family_id = new_family_id(district_code=payload.address.district_code, year=current_year)

    family = Family(
        family_id=family_id,
        status=FamilyStatusEnum.SUBMITTED,
        address_id=address.address_id,
        ration_card_number=payload.ration_card_number,
        ration_card_type=payload.ration_card_type,
        annual_income_amount=payload.annual_income_amount,
        income_band=payload.income_band,
        land_holding_acres=payload.land_holding_acres,
        house_type=payload.house_type,
        house_owned=payload.house_owned,
        has_lpg_connection=payload.has_lpg_connection,
        primary_occupation=payload.primary_occupation,
        registered_by=registered_by,
        registered_by_user_id=registered_by_user.user_id if registered_by_user else None,
    )
    db.add(family)
    db.commit()

    # 3. Create Head Person & Membership
    created_people = []
    head_p = Person(
        full_name=payload.head.full_name,
        dob=payload.head.dob,
        gender=payload.head.gender,
        marital_status=payload.head.marital_status,
        mobile=payload.head.mobile,
        social_category=payload.head.social_category,
        education_level=payload.head.education_level,
        occupation_type=payload.head.occupation_type,
        has_bank_account=payload.head.has_bank_account,
    )
    db.add(head_p)
    db.commit()
    db.refresh(head_p)
    created_people.append(head_p)

    head_m = FamilyMembership(
        person_id=head_p.person_id,
        family_id=family.family_id,
        role_in_family=RoleInFamilyEnum.HEAD,
        relation_to_head=payload.head.relation_to_head,
        start_date=date.today(),
    )
    db.add(head_m)

    # Consent record for Head
    db.add(
        ConsentRecord(
            person_id=head_p.person_id,
            purpose="REGISTRATION",
            mandatory=True,
        )
    )

    # Create or update active Citizen UserAccount for Head of Household if mobile exists
    if payload.head.mobile:
        pwd = payload.password if (payload.password and len(payload.password.strip()) >= 6) else "ClaimPassword@123"
        account_status = UserAccountStatusEnum.ACTIVE if registered_by == RegisteredByEnum.SELF else UserAccountStatusEnum.PENDING_CLAIM
        existing_acc = db.query(UserAccount).filter(UserAccount.login_id == payload.head.mobile).first()
        if existing_acc:
            existing_acc.person_id = head_p.person_id
            existing_acc.password_hash = hash_password(pwd)
            existing_acc.status = account_status
            existing_acc.role = UserRoleEnum.CITIZEN_HEAD
        else:
            db.add(
                UserAccount(
                    person_id=head_p.person_id,
                    login_id=payload.head.mobile,
                    password_hash=hash_password(pwd),
                    role=UserRoleEnum.CITIZEN_HEAD,
                    status=account_status,
                )
            )

    # 4. Create Members & Memberships
    for m in payload.members:
        # Calculate age
        today = date.today()
        m_age = today.year - m.dob.year - ((today.month, today.day) < (m.dob.month, m.dob.day))
        role = RoleInFamilyEnum.ADULT if m_age >= 18 else RoleInFamilyEnum.DEPENDENT

        mp = Person(
            full_name=m.full_name,
            dob=m.dob,
            gender=m.gender,
            marital_status=m.marital_status,
            mobile=m.mobile,
            social_category=m.social_category,
            education_level=m.education_level,
            occupation_type=m.occupation_type,
            has_bank_account=m.has_bank_account,
        )
        db.add(mp)
        db.commit()
        created_people.append(mp)

        db.add(
            FamilyMembership(
                person_id=mp.person_id,
                family_id=family.family_id,
                role_in_family=role,
                relation_to_head=m.relation_to_head,
                start_date=date.today(),
            )
        )
        db.add(ConsentRecord(person_id=mp.person_id, purpose="REGISTRATION", mandatory=True))

    db.commit()
    db.refresh(family)

    # Run non-destructive fuzzy duplicate checks once all household records exist.
    # Exact Aadhaar collisions remain hard-blocked at e-KYC confirmation.
    for person in created_people:
        run_duplicate_check_for_person(db, person)

    # 5. Write Audit
    write_audit(
        db=db,
        actor_user_id=registered_by_user.user_id if registered_by_user else None,
        actor_role=registered_by_user.role.value if registered_by_user else "CITIZEN_UNAUTH",
        action="CREATE_FAMILY",
        entity_type="family",
        entity_id=family.family_id,
        family_id=family.family_id,
        purpose="New Family Household Registration",
    )

    return family


def get_family_details(db: Session, family_id: str) -> Optional[Family]:
    """Fetch family with address and membership details."""
    return db.query(Family).filter(Family.family_id == family_id).first()
