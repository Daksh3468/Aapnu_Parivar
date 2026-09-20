from datetime import date, datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.family import Family
from app.models.person import Person
from app.models.scheme import Scheme
from app.models.document import Document
from app.models.eligibility import SchemeEligibilityRecord
from app.models.enums import (
    EligibilityStatusEnum,
    DocumentStatusEnum,
    DocumentTypeEnum,
    OccupationTypeEnum,
    GenderEnum,
)
from app.schemas.eligibility import SchemeEligibilityResponseSchema, RuleEvaluationDetail


class EligibilityEngine:
    """
    Evaluates household eligibility rules against all active welfare schemes.
    """

    @staticmethod
    def _age(person: Person) -> int:
        today = date.today()
        return today.year - person.dob.year - ((today.month, today.day) < (person.dob.month, person.dob.day))

    @staticmethod
    def evaluate_family_against_scheme(
        family: Family,
        scheme: Scheme,
        verified_docs: List[DocumentTypeEnum]
    ) -> Dict[str, Any]:
        """
        Evaluates a single family against a specific scheme.
        Returns dict with status, missing_documents, and evaluation_details.
        """
        details: List[RuleEvaluationDetail] = []
        missing_docs: List[str] = []
        is_rule_passed = True

        # 1. Income Evaluation
        max_income = getattr(scheme, "max_annual_income", None)
        if max_income is not None:
            income = float(family.annual_income_amount or 0.0)
            max_inc = float(max_income)
            if income <= max_inc:
                details.append(RuleEvaluationDetail(
                    rule_name="Income Threshold",
                    passed=True,
                    description=f"Household annual income ₹{income:,.2f} is within limit of ₹{max_inc:,.2f}"
                ))
            else:
                is_rule_passed = False
                details.append(RuleEvaluationDetail(
                    rule_name="Income Threshold",
                    passed=False,
                    description=f"Household annual income ₹{income:,.2f} exceeds max limit ₹{max_inc:,.2f}"
                ))

        # 2. Land Holding Evaluation
        max_land = getattr(scheme, "max_land_acres", None)
        if max_land is not None:
            land = float(family.land_holding_acres or 0.0)
            max_l = float(max_land)
            if land <= max_l:
                details.append(RuleEvaluationDetail(
                    rule_name="Land Holding Limit",
                    passed=True,
                    description=f"Household land holding {land} acres is within limit of {max_l} acres"
                ))
            else:
                is_rule_passed = False
                details.append(RuleEvaluationDetail(
                    rule_name="Land Holding Limit",
                    passed=False,
                    description=f"Household land holding {land} acres exceeds max limit {max_l} acres"
                ))

        # 3. Social Category Evaluation
        target_cats = getattr(scheme, "target_social_categories", None)
        if target_cats:
            member_categories = {
                m.person.social_category for m in family.memberships if m.end_date is None and m.person
            }
            allowed = set(target_cats)
            if member_categories.intersection(allowed) or "ALL" in allowed:
                details.append(RuleEvaluationDetail(
                    rule_name="Social Category Criteria",
                    passed=True,
                    description=f"Household category ({', '.join([c.value for c in member_categories if c])}) matches scheme criteria"
                ))
            else:
                is_rule_passed = False
                details.append(RuleEvaluationDetail(
                    rule_name="Social Category Criteria",
                    passed=False,
                    description=f"Scheme restricted to {', '.join(target_cats)}, but household has none"
                ))

        # 4. Special Scheme Specific Rules
        code = scheme.code.upper()
        
        # Namo Lakshmi / Female Education check
        if "NAMO" in code or "GIRL" in code or "LAKSHMI" in code:
            has_female_teen = False
            for m in family.memberships:
                if m.end_date is None and m.person:
                    age = EligibilityEngine._age(m.person)
                    if m.person.gender == GenderEnum.FEMALE and (13 <= age <= 20):
                        has_female_teen = True
                        break
            if has_female_teen:
                details.append(RuleEvaluationDetail(
                    rule_name="Demographic Criteria",
                    passed=True,
                    description="Household has eligible female student in high school age bracket (13-20 yrs)"
                ))
            else:
                is_rule_passed = False
                details.append(RuleEvaluationDetail(
                    rule_name="Demographic Criteria",
                    passed=False,
                    description="No female member in high school age bracket (13-20 yrs) found in household"
                ))

        # Senior Citizen / Old Age Pension
        if "PENSION" in code or "SENIOR" in code or "VAY" in code:
            has_senior = False
            for m in family.memberships:
                if m.end_date is None and m.person and EligibilityEngine._age(m.person) >= 60:
                    has_senior = True
                    break
            if has_senior:
                details.append(RuleEvaluationDetail(
                    rule_name="Senior Citizen Criteria",
                    passed=True,
                    description="Household contains at least one senior citizen member (age 60+)"
                ))
            else:
                is_rule_passed = False
                details.append(RuleEvaluationDetail(
                    rule_name="Senior Citizen Criteria",
                    passed=False,
                    description="No senior citizen (age 60+) present in household"
                ))

        # Shramik / Worker Scheme
        if "SHRAMIK" in code or "LABOUR" in code or "WORKER" in code:
            if family.primary_occupation in [OccupationTypeEnum.LABOUR, OccupationTypeEnum.FARMER, OccupationTypeEnum.ARTISAN]:
                details.append(RuleEvaluationDetail(
                    rule_name="Occupation Criteria",
                    passed=True,
                    description=f"Primary occupation ({family.primary_occupation.value}) is eligible for worker benefits"
                ))
            else:
                is_rule_passed = False
                details.append(RuleEvaluationDetail(
                    rule_name="Occupation Criteria",
                    passed=False,
                    description=f"Primary occupation ({family.primary_occupation.value}) is not listed under unorganized labor"
                ))

        # Default rule if no specific rules triggered
        if not details:
            details.append(RuleEvaluationDetail(
                rule_name="General Criteria",
                passed=True,
                description="Household meets general Gujarat resident registration criteria"
            ))

        # 5. Check Required Verified Documents
        req_docs = getattr(scheme, "required_documents", None)
        if req_docs:
            for doc_req in req_docs:
                matching = [d for d in verified_docs if d.value == doc_req or d.name == doc_req]
                if not matching:
                    missing_docs.append(doc_req)

        # Compute Final Status
        if not is_rule_passed:
            final_status = EligibilityStatusEnum.AUTO_INELIGIBLE
        elif missing_docs:
            final_status = EligibilityStatusEnum.DOCS_NEEDED
        else:
            final_status = EligibilityStatusEnum.AUTO_ELIGIBLE

        return {
            "status": final_status,
            "missing_documents": missing_docs,
            "evaluation_details": [d.model_dump() for d in details],
        }

    @staticmethod
    def evaluate_all_schemes_for_family(db: Session, family_id: str) -> List[SchemeEligibilityResponseSchema]:
        """
        Runs eligibility engine for a family across all active schemes in DB.
        """
        family = db.query(Family).filter(Family.family_id == family_id).first()
        if not family:
            return []

        schemes = db.query(Scheme).filter(Scheme.is_active == True).all()
        
        # Get list of verified document types for this family
        verified_docs = [
            doc.document_type
            for doc in db.query(Document).filter(
                Document.family_id == family_id,
                Document.status == DocumentStatusEnum.VERIFIED
            ).all()
        ]

        # Fetch existing persistent eligibility records (officer reviews / saved evaluations)
        existing_records = {
            r.scheme_id: r
            for r in db.query(SchemeEligibilityRecord).filter(SchemeEligibilityRecord.family_id == family_id).all()
        }

        results: List[SchemeEligibilityResponseSchema] = []

        for scheme in schemes:
            rec = existing_records.get(scheme.scheme_id)

            # If officer has manually reviewed, preserve officer status
            if rec and rec.status in [EligibilityStatusEnum.OFFICER_APPROVED, EligibilityStatusEnum.OFFICER_REJECTED]:
                status = rec.status
                missing_docs = rec.missing_documents or []
                details = rec.evaluation_details or []
                reviewed_by = rec.reviewed_by_user_id
                reviewed_at = rec.reviewed_at
                notes = rec.officer_notes
            else:
                eval_res = EligibilityEngine.evaluate_family_against_scheme(family, scheme, verified_docs)
                status = eval_res["status"]
                missing_docs = eval_res["missing_documents"]
                details = eval_res["evaluation_details"]
                reviewed_by = None
                reviewed_at = None
                notes = None

                # Persist or update record in DB
                if not rec:
                    rec = SchemeEligibilityRecord(
                        family_id=family_id,
                        scheme_id=scheme.scheme_id,
                        status=status,
                        missing_documents=missing_docs,
                        evaluation_details=details,
                    )
                    db.add(rec)
                else:
                    rec.status = status
                    rec.missing_documents = missing_docs
                    rec.evaluation_details = details
                    rec.evaluated_at = datetime.utcnow()

        db.commit()

        # Re-query joined schemas for clean response
        for scheme in schemes:
            rec = db.query(SchemeEligibilityRecord).filter(
                SchemeEligibilityRecord.family_id == family_id,
                SchemeEligibilityRecord.scheme_id == scheme.scheme_id
            ).first()

            results.append(SchemeEligibilityResponseSchema(
                scheme_id=scheme.scheme_id,
                scheme_code=scheme.code,
                scheme_name=scheme.name,
                category_name=scheme.category.name if scheme.category else "General",
                level=scheme.level,
                benefit_type=scheme.benefit_type,
                benefit_summary=scheme.benefit_summary,
                official_url=scheme.official_url,
                status=rec.status if rec else EligibilityStatusEnum.AUTO_INELIGIBLE,
                missing_documents=rec.missing_documents or [] if rec else [],
                evaluation_details=[RuleEvaluationDetail(**d) for d in (rec.evaluation_details or [])] if rec else [],
                reviewed_by_user_id=rec.reviewed_by_user_id if rec else None,
                reviewed_at=rec.reviewed_at if rec else None,
                officer_notes=rec.officer_notes if rec else None,
            ))

        return results
