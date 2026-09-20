from typing import List, Optional
from sqlalchemy.orm import Query
from sqlalchemy import or_
from app.models.user import UserAccount, OfficerJurisdiction
from app.models.enums import UserRoleEnum, JurisdictionScopeEnum
from app.models.family import Family
from app.models.address import Address


class JurisdictionScope:
    def __init__(self, is_statewide: bool = False, district_codes: List[int] = None, pincodes: List[str] = None):
        self.is_statewide = is_statewide
        self.district_codes = district_codes or []
        self.pincodes = pincodes or []


def build_officer_jurisdiction_scope(user: UserAccount) -> JurisdictionScope:
    """Build jurisdiction scope object from user's OfficerJurisdiction records."""
    if user.role == UserRoleEnum.STATE_ADMIN or user.role == UserRoleEnum.AUDITOR:
        return JurisdictionScope(is_statewide=True)

    if not user.jurisdictions:
        # A missing assignment must never silently expand an officer's access.
        return JurisdictionScope(is_statewide=False)

    district_codes = []
    pincodes = []
    is_statewide = False

    for j in user.jurisdictions:
        if j.scope_type == JurisdictionScopeEnum.STATE:
            is_statewide = True
            break
        elif j.scope_type == JurisdictionScopeEnum.DISTRICT and j.district_code is not None:
            district_codes.append(j.district_code)
        elif j.scope_type == JurisdictionScopeEnum.PINCODE and j.pincode:
            pincodes.append(j.pincode)

    if is_statewide:
        return JurisdictionScope(is_statewide=True)

    return JurisdictionScope(is_statewide=False, district_codes=district_codes, pincodes=pincodes)


def apply_family_jurisdiction_filter(query: Query, scope: JurisdictionScope) -> Query:
    """
    Apply officer jurisdiction filtering to a Family SQLAlchemy Query.
    Joins with Address to filter by district_code or pincode.
    """
    if scope.is_statewide:
        return query

    # Ensure Address is joined
    query = query.join(Address, Family.address_id == Address.address_id)

    conditions = []
    if scope.district_codes:
        conditions.append(Address.district_code.in_(scope.district_codes))
    if scope.pincodes:
        conditions.append(Address.pincode.in_(scope.pincodes))

    if conditions:
        query = query.filter(or_(*conditions))
    else:
        # If restricted officer has 0 scope configured, block all results
        query = query.filter(False)

    return query
