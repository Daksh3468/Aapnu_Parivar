from datetime import datetime
from typing import Tuple, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.person import Person
from app.models.enums import VerificationStatusEnum
from app.connectors.mock_uidai import mock_uidai
from app.utils.aadhaar import hash_aadhaar
from app.services.duplicate_service import check_exact_aadhaar_duplicate
from app.services.audit_service import write_audit


def start_member_aadhaar_verification(
    db: Session,
    person_id: str,
    aadhaar_number: str,
) -> Tuple[bool, str, Optional[str]]:
    """
    Step 1: Check duplicate Aadhaar hash and send mock e-KYC OTP.
    Full Aadhaar number is NEVER saved.
    """
    person = db.query(Person).filter(Person.person_id == person_id).first()
    if not person:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found.")

    # 1. Exact Aadhaar Hash Duplicate Check
    dup_person = check_exact_aadhaar_duplicate(db, aadhaar_number, exclude_person_id=person_id)
    if dup_person:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This Aadhaar identity is already verified under another active household. Please request a household transfer or split.",
        )

    # 2. Trigger mock UIDAI e-KYC OTP
    success, message, demo_otp = mock_uidai.start_ekyc(aadhaar_number)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)

    return True, message, demo_otp


def confirm_member_aadhaar_verification(
    db: Session,
    person_id: str,
    aadhaar_number: str,
    otp_code: str,
    actor_user_id: Optional[str] = None,
) -> Person:
    """
    Step 2: Verify e-KYC OTP, store last 4 digits & HMAC-SHA-256 hash, mark VERIFIED.
    """
    person = db.query(Person).filter(Person.person_id == person_id).first()
    if not person:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found.")

    # Confirm OTP with mock UIDAI connector
    success, message, ekyc_data = mock_uidai.confirm_ekyc(aadhaar_number, otp_code)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)

    # Store HMAC-SHA-256 hash and last 4 digits ONLY
    clean_aadhaar = aadhaar_number.strip().replace(" ", "").replace("-", "")
    person.aadhaar_last4 = clean_aadhaar[-4:]
    person.aadhaar_hash = hash_aadhaar(clean_aadhaar)
    person.verification_status = VerificationStatusEnum.VERIFIED
    person.verified_at = datetime.utcnow()

    db.commit()
    db.refresh(person)

    # Write Audit
    write_audit(
        db=db,
        actor_user_id=actor_user_id,
        actor_role="CITIZEN",
        action="VERIFY_AADHAAR",
        entity_type="person",
        entity_id=person.person_id,
        purpose="Aadhaar e-KYC Identity Verification",
    )

    return person
