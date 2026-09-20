import re
import secrets
from typing import Set

_d = [
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    [1, 2, 3, 4, 0, 6, 7, 8, 9, 5],
    [2, 3, 4, 0, 1, 7, 8, 9, 5, 6],
    [3, 4, 0, 1, 2, 8, 9, 5, 6, 7],
    [4, 0, 1, 2, 3, 9, 5, 6, 7, 8],
    [5, 9, 8, 7, 6, 0, 4, 3, 2, 1],
    [6, 5, 9, 8, 7, 1, 0, 4, 3, 2],
    [7, 6, 5, 9, 8, 2, 1, 0, 4, 3],
    [8, 7, 6, 5, 9, 3, 2, 1, 0, 4],
    [9, 8, 7, 6, 5, 4, 3, 2, 1, 0],
]

_p = [
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    [1, 5, 7, 6, 2, 8, 3, 0, 9, 4],
    [5, 8, 0, 3, 7, 9, 6, 1, 4, 2],
    [8, 9, 1, 6, 0, 4, 3, 5, 2, 7],
    [9, 4, 5, 3, 1, 2, 6, 8, 7, 0],
    [4, 2, 8, 6, 5, 7, 3, 9, 0, 1],
    [2, 7, 9, 3, 8, 0, 6, 4, 1, 5],
    [7, 0, 4, 6, 9, 1, 3, 2, 5, 8],
]

_inv = [0, 4, 3, 2, 1, 5, 6, 7, 8, 9]


def verhoeff_check_digit(num: str) -> str:
    """Calculate the Verhoeff check digit for a string of numeric digits."""
    c = 0
    for i, ch in enumerate(reversed(num)):
        c = _d[c][_p[(i + 1) % 8][int(ch)]]
    return str(_inv[c])


def verhoeff_valid(num: str) -> bool:
    """Validate a numeric string containing its check digit using Verhoeff algorithm."""
    if not num or not num.isdigit():
        return False
    c = 0
    for i, ch in enumerate(reversed(num)):
        c = _d[c][_p[i % 8][int(ch)]]
    return c == 0


def new_family_id(district_code: int, year: int, taken: Set[str] = None) -> str:
    """
    Generate a 12-digit formatted Family ID: GJ-DD-YY-SSSSSSS-C
    Example: GJ-07-26-4831927-1
    """
    if taken is None:
        taken = set()

    while True:
        serial = f"{secrets.randbelow(10**7):07d}"
        body = f"{district_code:02d}{year % 100:02d}{serial}"
        check = verhoeff_check_digit(body)
        fid = f"GJ-{body[:2]}-{body[2:4]}-{body[4:]}-{check}"
        if fid not in taken:
            return fid


def is_valid_family_id(fid: str) -> bool:
    """
    Validate a Family ID string format and Verhoeff check digit.
    Accepts formats with or without hyphens or spaces.
    """
    if not fid:
        return False

    cleaned = fid.upper().replace(" ", "").replace("-", "")
    if not cleaned.startswith("GJ"):
        return False

    digits = cleaned[2:]
    if len(digits) != 12:
        return False

    return verhoeff_valid(digits)
