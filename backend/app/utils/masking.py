def mask_mobile(mobile: str) -> str:
    """Mask mobile number e.g., 9876543210 -> 98XXXXXX10"""
    if not mobile or len(mobile) < 10:
        return mobile or ""
    clean = mobile.strip()
    return f"{clean[:2]}XXXXXX{clean[-2:]}"


def mask_ration_card(card_no: str) -> str:
    """Mask ration card number e.g., GJ1234567890 -> GJXXXXXX7890"""
    if not card_no or len(card_no) < 6:
        return card_no or ""
    clean = card_no.strip()
    return f"{clean[:2]}XXXXXX{clean[-4:]}"


def mask_aadhaar_last4(aadhaar_last4: str) -> str:
    """Display Aadhaar last 4 digits e.g. XXXX-XXXX-1234"""
    if not aadhaar_last4 or len(aadhaar_last4) != 4:
        return "XXXX-XXXX-XXXX"
    return f"XXXX-XXXX-{aadhaar_last4}"
