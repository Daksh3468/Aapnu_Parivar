import uuid
from datetime import date
from sqlalchemy import Column, String, Date, Enum, ForeignKey, Index, CheckConstraint, text
from sqlalchemy.orm import relationship
from app.core.db import Base
from app.models.enums import RoleInFamilyEnum, RelationToHeadEnum, MembershipReasonEnum


class FamilyMembership(Base):
    __tablename__ = "family_membership"

    membership_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    person_id = Column(String(36), ForeignKey("person.person_id"), nullable=False, index=True)
    family_id = Column(String(20), ForeignKey("family.family_id"), nullable=False, index=True)

    role_in_family = Column(Enum(RoleInFamilyEnum), nullable=False, default=RoleInFamilyEnum.ADULT)
    relation_to_head = Column(Enum(RelationToHeadEnum), nullable=False, default=RelationToHeadEnum.SELF)

    start_date = Column(Date, nullable=False, default=date.today)
    end_date = Column(Date, nullable=True)

    start_reason = Column(Enum(MembershipReasonEnum), nullable=False, default=MembershipReasonEnum.REGISTRATION)
    end_reason = Column(Enum(MembershipReasonEnum), nullable=True)
    event_id = Column(String(36), nullable=True)

    person = relationship("Person", back_populates="memberships")
    family = relationship("Family", back_populates="memberships")

    __table_args__ = (
        # Partial unique index: A person has at most ONE active membership (end_date IS NULL)
        Index(
            "ux_membership_active_person",
            "person_id",
            unique=True,
            sqlite_where=text("end_date IS NULL"),
            postgresql_where=text("end_date IS NULL"),
        ),
        # Partial unique index: A family has at most ONE active head (end_date IS NULL and role_in_family = 'HEAD')
        Index(
            "ux_membership_active_head",
            "family_id",
            unique=True,
            sqlite_where=text("end_date IS NULL AND role_in_family = 'HEAD'"),
            postgresql_where=text("end_date IS NULL AND role_in_family = 'HEAD'"),
        ),
        # Date range validity check
        CheckConstraint("end_date IS NULL OR end_date >= start_date", name="chk_membership_dates"),
    )
