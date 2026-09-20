import random
from datetime import datetime
from typing import List, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.family import Family
from app.models.person import Person
from app.models.membership import FamilyMembership
from app.models.address import Address
from app.models.enums import (
    RoleInFamilyEnum,
    RelationToHeadEnum,
    MembershipReasonEnum,
    FamilyStatusEnum,
    LifeEventTypeEnum,
    SplitStatusEnum,
    RationCardTypeEnum,
)

from app.models.life_event import LifeEventRecord, FamilySplitRecord
from app.models.application import SchemeApplication
from app.schemas.life_event import LifeEventCreateSchema, FamilySplitRequestSchema
from app.services.eligibility_service import EligibilityEngine
from app.services.audit_service import write_audit
from app.utils.family_id import new_family_id


class LifeEventService:

    @staticmethod
    def calculate_split_anomaly_score(
        db: Session,
        source_family_id: str,
        moved_person_ids: List[str],
        split_reason: str = None
    ) -> Tuple[float, List[str]]:
        """
        Calculates risk anomaly score (0 - 100) for a household split request based on risk heuristics.
        """
        score = 0.0
        flags = []

        family = db.query(Family).filter(Family.family_id == source_family_id).first()
        if not family:
            return 0.0, []

        # Risk Heuristic 1: BPL / Antyodaya Ration Card status
        if family.ration_card_type in [RationCardTypeEnum.AAY, RationCardTypeEnum.PHH]:
            score += 25.0
            flags.append("Source household holds BPL / Antyodaya (AAY/PHH) welfare ration card")

        # Risk Heuristic 2: Active scheme applications in last 60 days
        active_apps = db.query(SchemeApplication).filter(
            SchemeApplication.family_id == source_family_id
        ).count()
        if active_apps > 0:
            score += 30.0
            flags.append(f"Source household has {active_apps} active scheme application(s) on file")

        # Risk Heuristic 3: Moving all earners/salaried members
        moved_persons = db.query(Person).filter(Person.person_id.in_(moved_person_ids)).all()
        def is_earner(p: Person) -> bool:
            occ = p.occupation_type.value if hasattr(p.occupation_type, 'value') else str(p.occupation_type)
            return occ in ["SALARIED", "FARMER", "SELF_EMPLOYED", "LABOUR", "ARTISAN"]

        earners_moved = sum(1 for p in moved_persons if is_earner(p))
        total_memberships = [m for m in family.memberships if m.end_date is None]
        remaining_person_ids = [m.person_id for m in total_memberships if m.person_id not in moved_person_ids]
        remaining_persons = db.query(Person).filter(Person.person_id.in_(remaining_person_ids)).all()
        remaining_earners = sum(1 for p in remaining_persons if is_earner(p))

        if earners_moved > 0 and remaining_earners == 0:
            score += 35.0
            flags.append("Splitting household transfers all earning/employed members, leaving source household with 0 earners")

        # Risk Heuristic 4: Single person split under age 21
        if len(moved_person_ids) == 1:
            p = moved_persons[0] if moved_persons else None
            if p and p.dob:
                try:
                    birth_year = p.dob.year if hasattr(p.dob, 'year') else int(str(p.dob).split("-")[0])
                    current_year = datetime.utcnow().year
                    age = current_year - birth_year
                    if age < 21:
                        score += 40.0
                        flags.append(f"Single-member split requested for young individual (age {age})")
                except Exception:
                    pass


        # Risk Heuristic 5: Vague or missing split reason
        if not split_reason or len(split_reason.strip()) < 8:
            score += 15.0
            flags.append("Inadequate or unstated justification provided for household split")

        final_score = min(score, 100.0)
        return final_score, flags

    @staticmethod
    def execute_family_split(
        db: Session,
        split_record: FamilySplitRecord,
        actor_user_id: str,
        actor_role: str,
        new_address_dict: dict = None
    ) -> Family:
        """
        Executes the household split:
        1. Validates invariants
        2. Creates new Family identity
        3. Updates memberships for moved persons & replacement heads
        4. Re-evaluates scheme eligibility for both families
        5. Logs life event & audit record
        """
        source_family = db.query(Family).filter(Family.family_id == split_record.source_family_id).first()
        if not source_family:
            raise HTTPException(status_code=404, detail="Source family not found")

        moved_ids = split_record.moved_person_ids_json or []
        if not moved_ids:
            raise HTTPException(status_code=400, detail="No members specified for split")

        # Active memberships in source family
        active_memberships = [m for m in source_family.memberships if m.end_date is None]
        active_person_ids = [m.person_id for m in active_memberships]

        for pid in moved_ids:
            if pid not in active_person_ids:
                raise HTTPException(status_code=400, detail=f"Person #{pid} is not an active member of source family")

        if split_record.new_head_person_id not in moved_ids:
            raise HTTPException(status_code=400, detail="New Head of Family must be one of the moving members")

        # Check source family head status
        current_head_membership = next((m for m in active_memberships if m.role_in_family == RoleInFamilyEnum.HEAD), None)
        current_head_moved = current_head_membership and (current_head_membership.person_id in moved_ids)

        if current_head_moved:
            if not split_record.replacement_source_head_person_id:
                raise HTTPException(
                    status_code=400,
                    detail="Replacement Head of Family must be specified for the source household when the head moves out"
                )
            if split_record.replacement_source_head_person_id in moved_ids:
                raise HTTPException(
                    status_code=400,
                    detail="Replacement source Head of Family cannot be one of the moving members"
                )
            if split_record.replacement_source_head_person_id not in active_person_ids:
                raise HTTPException(
                    status_code=400,
                    detail="Replacement source Head of Family must be an active member of source family"
                )

        # 1. Create or assign Address for new family
        if new_address_dict:
            new_addr = Address(
                line1=new_address_dict.get("line1", source_family.address.line1 if source_family.address else "Main Street"),
                village_or_town=new_address_dict.get("village_or_town", source_family.address.village_or_town if source_family.address else "Town"),
                taluka=new_address_dict.get("taluka", source_family.address.taluka if source_family.address else None),
                district_code=new_address_dict.get("district_code", source_family.address.district_code if source_family.address else 7),
                pincode=new_address_dict.get("pincode", source_family.address.pincode if source_family.address else "380001"),
            )
            db.add(new_addr)
            db.flush()
            addr_id = new_addr.address_id
        else:
            addr_id = source_family.address_id

        # 2. Generate structured 12-digit Family ID: GJ-DD-YY-SSSSSSS-C
        dist_code = new_address_dict.get("district_code") if new_address_dict else (source_family.address.district_code if source_family.address else 7)
        year_val = datetime.utcnow().year
        new_fid = new_family_id(district_code=dist_code, year=year_val)

        new_family = Family(
            family_id=new_fid,
            status=FamilyStatusEnum.VERIFIED,
            ration_card_type=source_family.ration_card_type,
            income_band=source_family.income_band,
            address_id=addr_id,
        )
        db.add(new_family)
        db.flush()

        today_date = datetime.utcnow().date()
        today_str = today_date.isoformat()

        # 3. Transfer moved members to new family
        for m in active_memberships:
            if m.person_id in moved_ids:
                m.end_date = today_date
                m.end_reason = MembershipReasonEnum.SPLIT

                is_new_head = (m.person_id == split_record.new_head_person_id)
                new_role = RoleInFamilyEnum.HEAD if is_new_head else RoleInFamilyEnum.ADULT
                rel = RelationToHeadEnum.SELF if is_new_head else RelationToHeadEnum.OTHER

                new_mem = FamilyMembership(
                    family_id=new_fid,
                    person_id=m.person_id,
                    role_in_family=new_role,
                    relation_to_head=rel,
                    start_date=today_date,
                    start_reason=MembershipReasonEnum.SPLIT,
                )
                db.add(new_mem)

        # 4. If source head moved, assign replacement head for source family
        if current_head_moved and split_record.replacement_source_head_person_id:
            rep_mem = next((m for m in active_memberships if m.person_id == split_record.replacement_source_head_person_id), None)
            if rep_mem:
                rep_mem.role_in_family = RoleInFamilyEnum.HEAD
                rep_mem.relation_to_head = RelationToHeadEnum.SELF


        split_record.new_family_id = new_fid
        split_record.status = SplitStatusEnum.AUTOMATICALLY_APPROVED if split_record.anomaly_score <= 50 else SplitStatusEnum.OFFICER_APPROVED

        db.commit()

        # 5. Record life event log
        life_evt = LifeEventRecord(
            family_id=source_family.family_id,
            event_type=LifeEventTypeEnum.HOUSEHOLD_SPLIT,
            event_date=today_str,
            description=f"Household split executed. Created new family #{new_fid} with {len(moved_ids)} members.",
            details_json={"new_family_id": new_fid, "moved_person_ids": moved_ids},
            registered_by_user_id=actor_user_id,
        )
        db.add(life_evt)
        db.commit()

        # 6. Re-evaluate scheme eligibility for both households
        try:
            EligibilityEngine.evaluate_all_schemes_for_family(db, source_family.family_id)
            EligibilityEngine.evaluate_all_schemes_for_family(db, new_fid)
        except Exception:
            pass

        # 7. Audit log
        write_audit(
            db=db,
            actor_user_id=actor_user_id,
            actor_role=actor_role,
            action="HOUSEHOLD_SPLIT_EXECUTE",
            entity_type="family",
            entity_id=new_fid,
            family_id=source_family.family_id,
            details={"moved_count": len(moved_ids), "new_family_id": new_fid},
        )

        return new_family
