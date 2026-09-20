from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.auth_deps import get_current_user
from app.models.user import UserAccount
from app.services.verification_service import (
    start_member_aadhaar_verification,
    confirm_member_aadhaar_verification,
)
from app.utils.masking import mask_aadhaar_last4

router = APIRouter()


class VerifyStartRequest(BaseModel):
    aadhaar_number: str = Field(..., pattern=r"^\d{12}$", description="12-digit Aadhaar number")


class VerifyStartResponse(BaseModel):
    message: str
    demo_otp: Optional[str] = None  # Returned in DEMO_MODE for banner


class VerifyConfirmRequest(BaseModel):
    aadhaar_number: str = Field(..., pattern=r"^\d{12}$")
    otp_code: str = Field(..., min_length=6, max_length=6)


class VerifyConfirmResponse(BaseModel):
    person_id: str
    full_name: str
    verification_status: str
    aadhaar_last4_masked: str
    verified_at: str


@router.post("/members/{person_id}/verify/start", response_model=VerifyStartResponse)
def start_verification(
    person_id: str,
    payload: VerifyStartRequest,
    db: Session = Depends(get_db),
):
    """
    Step 1: Start Aadhaar e-KYC verification process for a household member.
    Validates format, checks duplicate hash, and sends mock e-KYC OTP code.
    """
    success, message, demo_otp = start_member_aadhaar_verification(
        db=db,
        person_id=person_id,
        aadhaar_number=payload.aadhaar_number,
    )

    return VerifyStartResponse(message=message, demo_otp=demo_otp)


@router.post("/members/{person_id}/verify/confirm", response_model=VerifyConfirmResponse)
def confirm_verification(
    person_id: str,
    payload: VerifyConfirmRequest,
    db: Session = Depends(get_db),
):
    """
    Step 2: Confirm Aadhaar e-KYC OTP code.
    Stores HMAC-SHA-256 hash and last 4 digits ONLY. Full Aadhaar is NEVER stored.
    """
    person = confirm_member_aadhaar_verification(
        db=db,
        person_id=person_id,
        aadhaar_number=payload.aadhaar_number,
        otp_code=payload.otp_code,
    )

    return VerifyConfirmResponse(
        person_id=person.person_id,
        full_name=person.full_name,
        verification_status=person.verification_status.value,
        aadhaar_last4_masked=mask_aadhaar_last4(person.aadhaar_last4),
        verified_at=person.verified_at.strftime("%Y-%m-%d %H:%M:%S") if person.verified_at else "",
    )
