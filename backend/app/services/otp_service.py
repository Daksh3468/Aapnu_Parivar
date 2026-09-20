import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Tuple, Optional
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.user import OTPChallenge, UserAccount
from app.core.security import hash_password, verify_password


def create_otp_challenge(
    db: Session,
    target_mobile: str,
    purpose: str,  # LOGIN, RESET, CLAIM, AADHAAR_KYC
    user_id: Optional[str] = None,
) -> Tuple[OTPChallenge, str]:
    """
    Generate a 6-digit mock OTP challenge.
    In DEMO_MODE, returns the raw code to be displayed in the demo banner.
    Only the hash is stored in the database.
    """
    # 6-digit random code
    raw_code = f"{secrets.randbelow(900000) + 100000:06d}"
    
    # Hash code using hashlib sha256 for fast check
    code_hash = hashlib.sha256(raw_code.encode("utf-8")).hexdigest()
    expires_at = datetime.utcnow() + timedelta(minutes=5)

    challenge = OTPChallenge(
        user_id=user_id,
        target_mobile=target_mobile,
        purpose=purpose,
        code_hash=code_hash,
        expires_at=expires_at,
        attempts=0,
    )

    db.add(challenge)
    db.commit()
    db.refresh(challenge)

    return challenge, raw_code


def verify_otp_challenge(
    db: Session,
    target_mobile: str,
    purpose: str,
    submitted_code: str,
) -> Tuple[bool, str]:
    """
    Verify submitted OTP code against active challenge.
    Checks expiry, attempt count, and single-use invalidation.
    """
    challenge = (
        db.query(OTPChallenge)
        .filter(
            OTPChallenge.target_mobile == target_mobile,
            OTPChallenge.purpose == purpose,
            OTPChallenge.used_at.is_(None),
        )
        .order_by(OTPChallenge.expires_at.desc())
        .first()
    )

    if not challenge:
        return False, "No active OTP request found. Please request a new OTP."

    if datetime.utcnow() > challenge.expires_at:
        return False, "OTP has expired. Please request a new code."

    if challenge.attempts >= 3:
        return False, "Maximum attempts exceeded. Please request a new OTP."

    challenge.attempts += 1
    submitted_hash = hashlib.sha256(submitted_code.strip().encode("utf-8")).hexdigest()

    if submitted_hash != challenge.code_hash:
        db.commit()
        return False, f"Invalid OTP code. {3 - challenge.attempts} attempts remaining."

    # Mark OTP as used
    challenge.used_at = datetime.utcnow()
    db.commit()

    return True, "OTP verified successfully."
