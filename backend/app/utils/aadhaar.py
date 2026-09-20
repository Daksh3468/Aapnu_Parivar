import hmac
import hashlib
import secrets
from app.core.config import settings
from app.utils.family_id import verhoeff_check_digit, verhoeff_valid


def hash_aadhaar(aadhaar_number: str) -> str:
    """
    Compute a secure keyed HMAC-SHA-256 hash of the 12-digit Aadhaar number.
    Full Aadhaar numbers are never stored in the database.
    """
    if not aadhaar_number:
        return ""
    clean = aadhaar_number.strip().replace(" ", "").replace("-", "")
    key = settings.AADHAAR_HASH_KEY.encode("utf-8")
    return hmac.new(key, clean.encode("utf-8"), hashlib.sha256).hexdigest()


def generate_synthetic_aadhaar() -> str:
    """
    Generate a 12-digit synthetic Aadhaar number starting with '1' and valid Verhoeff check digit.
    Real Aadhaar numbers NEVER start with '1', preventing collision with real citizens.
    """
    body = f"1{secrets.randbelow(10**10):010d}"
    check = verhoeff_check_digit(body)
    return f"{body}{check}"


def is_valid_aadhaar_format(aadhaar_number: str) -> bool:
    """Validate 12-digit format and Verhoeff check digit."""
    if not aadhaar_number:
        return False
    clean = aadhaar_number.strip().replace(" ", "").replace("-", "")
    if len(clean) != 12 or not clean.isdigit():
        return False
    return verhoeff_valid(clean)
