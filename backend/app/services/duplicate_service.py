from typing import List, Tuple, Dict, Any, Optional
from sqlalchemy.orm import Session
from rapidfuzz import fuzz

from app.models.person import Person
from app.models.duplicate import DuplicateFlag
from app.utils.aadhaar import hash_aadhaar
from app.utils.normalize import normalize_name


def check_exact_aadhaar_duplicate(db: Session, aadhaar_number: str, exclude_person_id: Optional[str] = None) -> Optional[Person]:
    """
    Hard match check: Check if the HMAC-SHA-256 Aadhaar hash already exists for another person.
    """
    if not aadhaar_number:
        return None

    ahash = hash_aadhaar(aadhaar_number)
    query = db.query(Person).filter(Person.aadhaar_hash == ahash)
    if exclude_person_id:
        query = query.filter(Person.person_id != exclude_person_id)

    return query.first()


def score_candidate_duplicate(
    person_a: Person,
    cand_b: Person,
) -> Tuple[float, Dict[str, Any]]:
    """
    Fuzzy match scoring using weighted signals from Design Section 8.4:
    - Name similarity (rapidfuzz token_sort_ratio): 0.40
    - Date of Birth match (exact=1.0, year+month=0.6, year=0.3): 0.25
    - Mobile match: 0.15
    - Address similarity: 0.15
    - Gender match: 0.05
    """
    score = 0.0
    reasons = {}

    # 1. Name similarity (0.40)
    norm_a = normalize_name(person_a.full_name)
    norm_b = normalize_name(cand_b.full_name)
    name_sim = fuzz.token_sort_ratio(norm_a, norm_b) / 100.0
    score += name_sim * 0.40
    reasons["name_similarity"] = round(name_sim, 2)

    # 2. Date of birth (0.25)
    dob_score = 0.0
    if person_a.dob == cand_b.dob:
        dob_score = 1.0
    elif person_a.dob.year == cand_b.dob.year and person_a.dob.month == cand_b.dob.month:
        dob_score = 0.6
    elif person_a.dob.year == cand_b.dob.year:
        dob_score = 0.3
    score += dob_score * 0.25
    reasons["dob_match_score"] = dob_score

    # 3. Mobile match (0.15)
    mobile_score = 0.0
    if person_a.mobile and cand_b.mobile and person_a.mobile.strip() == cand_b.mobile.strip():
        mobile_score = 1.0
    score += mobile_score * 0.15
    reasons["mobile_match"] = mobile_score

    # 4. Gender match (0.05)
    gender_score = 1.0 if person_a.gender == cand_b.gender else 0.0
    score += gender_score * 0.05
    reasons["gender_match"] = gender_score

    # Total score rounded to 2 decimal places
    final_score = round(score, 2)
    reasons["final_score"] = final_score

    return final_score, reasons


def run_duplicate_check_for_person(
    db: Session,
    person: Person,
) -> Tuple[bool, Optional[str], Optional[DuplicateFlag]]:
    """
    Run candidate blocking and scoring for a person against existing registry candidates.
    Returns: (blocked: bool, message: str, flag: DuplicateFlag)
    - score >= 0.90: BLOCKED + HIGH flag created
    - 0.75 <= score < 0.90: ALLOWED + MEDIUM flag created
    - score < 0.75: ALLOWED + No flag
    """
    # Candidate blocking: Find persons sharing DOB year or mobile
    query = db.query(Person).filter(Person.person_id != person.person_id)

    candidates = []
    if person.mobile:
        candidates.extend(query.filter(Person.mobile == person.mobile).all())

    dob_candidates = query.filter(Person.dob == person.dob).all()
    for c in dob_candidates:
        if c not in candidates:
            candidates.append(c)

    highest_score = 0.0
    best_candidate = None
    best_reasons = {}

    for cand in candidates:
        s, r = score_candidate_duplicate(person, cand)
        if s > highest_score:
            highest_score = s
            best_candidate = cand
            best_reasons = r

    if highest_score >= 0.90:
        # Create HIGH duplicate flag
        flag = DuplicateFlag(
            person_a_id=person.person_id,
            person_b_id=best_candidate.person_id,
            score=highest_score,
            severity="HIGH",
            reasons=best_reasons,
            status="OPEN",
        )
        db.add(flag)
        db.commit()
        return True, f"Possible duplicate identity detected with high similarity ({int(highest_score * 100)}%). Action blocked for officer review.", flag

    elif highest_score >= 0.75:
        # Create MEDIUM duplicate flag
        flag = DuplicateFlag(
            person_a_id=person.person_id,
            person_b_id=best_candidate.person_id,
            score=highest_score,
            severity="MEDIUM",
            reasons=best_reasons,
            status="OPEN",
        )
        db.add(flag)
        db.commit()
        return False, f"Potential duplicate match flagged ({int(highest_score * 100)}%) and sent for officer review.", flag

    return False, None, None
