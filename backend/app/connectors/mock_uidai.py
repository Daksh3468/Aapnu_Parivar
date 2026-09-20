import secrets
from typing import Dict, Any, Tuple
from app.utils.family_id import verhoeff_valid
from app.utils.aadhaar import is_valid_aadhaar_format


class MockUIDAIConnector:
    """Mock Aadhaar e-KYC service adapter simulating UIDAI e-KYC OTP flow."""

    source_system = "UIDAI_EKYC"

    def __init__(self):
        # In-memory mock OTP challenges for demonstration
        self._challenges: Dict[str, str] = {}

    def start_ekyc(self, aadhaar_number: str) -> Tuple[bool, str, str]:
        """
        Validate Aadhaar format and generate a 6-digit mock e-KYC OTP.
        Returns: (success, message, mock_otp_code)
        """
        clean = aadhaar_number.strip().replace(" ", "").replace("-", "")
        if not is_valid_aadhaar_format(clean):
            return False, "Invalid Aadhaar number. Must be 12 digits with valid Verhoeff check digit.", ""

        raw_otp = f"{secrets.randbelow(900000) + 100000:06d}"
        self._challenges[clean] = raw_otp

        return True, f"Mock Aadhaar e-KYC OTP sent to registered mobile linked with XXXX-XXXX-{clean[-4:]}.", raw_otp

    def confirm_ekyc(self, aadhaar_number: str, otp_code: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Verify e-KYC OTP and return mock identity attributes.
        """
        clean = aadhaar_number.strip().replace(" ", "").replace("-", "")
        expected_otp = self._challenges.get(clean)

        if not expected_otp:
            return False, "No active e-KYC request found for this Aadhaar number.", {}

        if otp_code.strip() != expected_otp:
            return False, "Invalid e-KYC OTP code.", {}

        # Clear used OTP challenge
        del self._challenges[clean]

        # Return mock e-KYC demographic response
        ekyc_data = {
            "aadhaar_last4": clean[-4:],
            "name": "VERIFIED CITIZEN",
            "gender": "MALE",
            "ekyc_status": "SUCCESS",
        }

        return True, "Aadhaar e-KYC verification successful.", ekyc_data


mock_uidai = MockUIDAIConnector()
