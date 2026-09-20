import logging
from sqlalchemy.orm import Session
from app.core.db import SessionLocal
from app.core.security import hash_password
from app.models.user import UserAccount, OfficerJurisdiction
from app.models.enums import UserRoleEnum, UserAccountStatusEnum, JurisdictionScopeEnum

logger = logging.getLogger("aapnu_parivar")


def seed_demo_users():
    """Seed demo accounts for State Admin, District Officer, Field Officer, and Citizen."""
    db: Session = SessionLocal()
    try:
        demo_accounts = [
            {
                "login_id": "admin@gujarat.gov.in",
                "password": "Admin@123",
                "role": UserRoleEnum.STATE_ADMIN,
                "scope_type": JurisdictionScopeEnum.STATE,
                "district_code": None,
                "pincode": None,
            },
            {
                "login_id": "district07@gujarat.gov.in",
                "password": "District@123",
                "role": UserRoleEnum.DISTRICT_OFFICER,
                "scope_type": JurisdictionScopeEnum.DISTRICT,
                "district_code": 7,  # Bhavnagar
                "pincode": None,
            },
            {
                "login_id": "field0701@gujarat.gov.in",
                "password": "Field@123",
                "role": UserRoleEnum.FIELD_OFFICER,
                "scope_type": JurisdictionScopeEnum.PINCODE,
                "district_code": 7,
                "pincode": "364001",
            },
            {
                "login_id": "9876543210",
                "password": "Citizen@123",
                "role": UserRoleEnum.CITIZEN_HEAD,
                "scope_type": None,
                "district_code": None,
                "pincode": None,
            },
        ]

        for acc in demo_accounts:
            existing = db.query(UserAccount).filter(UserAccount.login_id == acc["login_id"]).first()
            if not existing:
                user = UserAccount(
                    login_id=acc["login_id"],
                    password_hash=hash_password(acc["password"]),
                    role=acc["role"],
                    status=UserAccountStatusEnum.ACTIVE,
                )
                db.add(user)
                db.commit()
                db.refresh(user)

                if acc["scope_type"]:
                    jurisdiction = OfficerJurisdiction(
                        user_id=user.user_id,
                        scope_type=acc["scope_type"],
                        district_code=acc["district_code"],
                        pincode=acc["pincode"],
                    )
                    db.add(jurisdiction)
                    db.commit()

                logger.info(f"Seeded user: {acc['login_id']} ({acc['role'].value})")

    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_users()
