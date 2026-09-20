import re

HONORIFICS = [
    "shri", "smt", "mr", "mrs", "ms", "dr", "bhai", "ben", "kumar",
    "patel", "shah", "ji", "master", "baby"
]

def normalize_name(name: str) -> str:
    """
    Normalize name string: lowercase, strip honorifics, strip special chars, collapse spaces.
    Example: 'Shri Rajeshkumar Patel' -> 'rajesh'
    """
    if not name:
        return ""

    cleaned = name.lower()
    cleaned = re.sub(r"[^\w\s]", " ", cleaned)

    tokens = cleaned.split()
    filtered = [t for t in tokens if t not in HONORIFICS and len(t) > 1]

    return " ".join(filtered) if filtered else cleaned.strip()


def normalize_address(address: str) -> str:
    """Normalize address string: lowercase, strip punctuation, collapse whitespace."""
    if not address:
        return ""
    cleaned = address.lower()
    cleaned = re.sub(r"[^\w\s]", " ", cleaned)
    return " ".join(cleaned.split())
