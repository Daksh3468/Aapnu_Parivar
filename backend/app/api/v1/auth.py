from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.config import settings
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.core.auth_deps import get_current_user, get_active_citizen_membership
from app.models.user import UserAccount
from app.models.enums import UserRoleEnum, UserAccountStatusEnum, RoleInFamilyEnum
from app.services.otp_service import create_otp_challenge, verify_otp_challenge
from app.services.audit_service import write_audit

router = APIRouter()


# Request / Response Schemas
class LoginRequest(BaseModel):
    login_id: str = Field(..., description="Mobile number for citizen, or email/username for officer")
    password: Optional[str] = None
    otp_code: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: str
    role: str
    person_id: Optional[str] = None
    family_id: Optional[str] = None


class OTPRequestPayload(BaseModel):
    mobile: str
    purpose: str = "LOGIN"  # LOGIN, RESET, CLAIM


class OTPResponse(BaseModel):
    message: str
    demo_otp: Optional[str] = None  # Returned in DEMO_MODE for banner


class OTPVerifyPayload(BaseModel):
    mobile: str
    purpose: str
    code: str


class PasswordResetPayload(BaseModel):
    mobile: str
    otp_code: str
    new_password: str


class ChangePasswordPayload(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=6)


class UserMeResponse(BaseModel):
    user_id: str
    login_id: str
    role: str
    status: str
    person_id: Optional[str] = None
    family_id: Optional[str] = None
    is_head: bool = False


# Endpoints
@router.post("/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    """Log in with mobile + password, email + password, or mobile + OTP."""
    user = db.query(UserAccount).filter(UserAccount.login_id == payload.login_id.strip()).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials or account not found.",
        )

    if user.status != UserAccountStatusEnum.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account status is '{user.status.value}'. Please contact support.",
        )

    # 1. OTP Authentication path
    if payload.otp_code:
        success, msg = verify_otp_challenge(
            db=db,
            target_mobile=payload.login_id.strip(),
            purpose="LOGIN",
            submitted_code=payload.otp_code,
        )
        if not success:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg)
    # 2. Password Authentication path
    elif payload.password:
        if not verify_password(payload.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid password.",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either password or OTP code must be provided.",
        )

    # Resolve active family & citizen role dynamically
    membership = get_active_citizen_membership(user, db)
    resolved_role = user.role.value
    family_id = None

    if membership:
        family_id = membership.family_id
        if membership.role_in_family == RoleInFamilyEnum.HEAD:
            resolved_role = UserRoleEnum.CITIZEN_HEAD.value
        else:
            resolved_role = UserRoleEnum.CITIZEN_MEMBER.value

    # Issue Tokens
    access_token = create_access_token(
        subject=user.login_id,
        role=resolved_role,
        user_id=user.user_id,
        person_id=user.person_id,
        family_id=family_id,
    )
    refresh_token = create_refresh_token(user_id=user.user_id)

    # Write Audit Log
    write_audit(
        db=db,
        actor_user_id=user.user_id,
        actor_role=resolved_role,
        action="LOGIN",
        entity_type="user_account",
        entity_id=user.user_id,
        family_id=family_id,
        purpose="User authentication login",
        ip_address=request.client.host if request.client else None,
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user_id=user.user_id,
        role=resolved_role,
        person_id=user.person_id,
        family_id=family_id,
    )


@router.post("/auth/otp/request", response_model=OTPResponse)
def request_otp(payload: OTPRequestPayload, db: Session = Depends(get_db)):
    """Request a mock 6-digit OTP challenge."""
    challenge, raw_code = create_otp_challenge(
        db=db,
        target_mobile=payload.mobile.strip(),
        purpose=payload.purpose,
    )

    demo_code = raw_code if settings.DEMO_MODE else None

    return OTPResponse(
        message=f"OTP code sent to {payload.mobile[:2]}XXXXXX{payload.mobile[-2:]}.",
        demo_otp=demo_code,
    )


@router.post("/auth/otp/verify")
def verify_otp(payload: OTPVerifyPayload, db: Session = Depends(get_db)):
    """Verify an active OTP challenge."""
    success, msg = verify_otp_challenge(
        db=db,
        target_mobile=payload.mobile.strip(),
        purpose=payload.purpose,
        submitted_code=payload.code,
    )
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

    return {"message": msg, "verified": True}


@router.post("/auth/password/reset")
def reset_password(payload: PasswordResetPayload, db: Session = Depends(get_db)):
    """Reset password using OTP verification."""
    success, msg = verify_otp_challenge(
        db=db,
        target_mobile=payload.mobile.strip(),
        purpose="RESET",
        submitted_code=payload.otp_code,
    )
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

    user = db.query(UserAccount).filter(UserAccount.login_id == payload.mobile.strip()).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User account not found.")

    user.password_hash = hash_password(payload.new_password)
    db.commit()

    return {"message": "Password reset successfully. You can now log in with your new password."}


@router.post("/auth/password/change")
def change_password(
    payload: ChangePasswordPayload,
    request: Request,
    current_user: UserAccount = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Authenticated endpoint allowing logged-in user to change their password."""
    if not verify_password(payload.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect.",
        )

    if len(payload.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 6 characters long.",
        )

    current_user.password_hash = hash_password(payload.new_password)
    db.commit()

    write_audit(
        db=db,
        actor_user_id=current_user.user_id,
        actor_role=current_user.role.value,
        action="CHANGE_PASSWORD",
        entity_type="user_account",
        entity_id=current_user.user_id,
        purpose="User changed account password",
        ip_address=request.client.host if request.client else None,
    )

    return {"message": "Password changed successfully."}


@router.get("/auth/me", response_model=UserMeResponse)
def get_me(current_user: UserAccount = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get current authenticated user profile."""
    membership = get_active_citizen_membership(current_user, db)
    family_id = membership.family_id if membership else None
    is_head = membership.role_in_family == RoleInFamilyEnum.HEAD if membership else False

    return UserMeResponse(
        user_id=current_user.user_id,
        login_id=current_user.login_id,
        role=current_user.role.value,
        status=current_user.status.value,
        person_id=current_user.person_id,
        family_id=family_id,
        is_head=is_head,
    )
