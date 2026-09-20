from typing import List, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.core.security import decode_token
from app.models.user import UserAccount
from app.models.enums import UserRoleEnum
from app.models.membership import FamilyMembership

security_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: Session = Depends(get_db),
) -> UserAccount:
    """FastAPI dependency: Extract and validate JWT bearer token."""
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials missing.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_token(credentials.credentials)
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("user_id")
    user = db.query(UserAccount).filter(UserAccount.user_id == user_id).first()

    if not user or user.status.value != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive or disabled.",
        )

    return user


def require_roles(allowed_roles: List[UserRoleEnum]):
    """FastAPI dependency factory: Enforce role-based access control."""
    def role_checker(current_user: UserAccount = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted for role '{current_user.role.value}'.",
            )
        return current_user

    return role_checker


def get_active_citizen_membership(
    user: UserAccount,
    db: Session,
) -> Optional[FamilyMembership]:
    """Helper: Retrieve citizen's active family membership."""
    if not user.person_id:
        return None

    return (
        db.query(FamilyMembership)
        .filter(
            FamilyMembership.person_id == user.person_id,
            FamilyMembership.end_date.is_(None),
        )
        .first()
    )
