import json
import os
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.scheme import SchemeCategory, Scheme, SchemeLevelEnum, BenefitTypeEnum, EligibilityUnitEnum
from app.connectors.registry import connector_registry

logger = logging.getLogger("aapnu_parivar")


def sync_all_schemes_and_categories(db: Session) -> int:
    """
    Idempotently sync categories & schemes into database from master fixture and connectors.
    Returns count of updated/created schemes.
    """
    fixture_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "fixtures", "schemes.json"
    )

    if not os.path.exists(fixture_path):
        logger.error(f"Scheme fixture file not found at {fixture_path}")
        return 0

    with open(fixture_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 1. Sync Categories
    for c in data.get("categories", []):
        cat = db.query(SchemeCategory).filter(SchemeCategory.category_id == c["category_id"]).first()
        if not cat:
            db.add(SchemeCategory(
                category_id=c["category_id"],
                name=c["name"],
                icon_name=c.get("icon_name", "Layers"),
            ))
        else:
            cat.name = c["name"]
            cat.icon_name = c.get("icon_name", cat.icon_name)

    db.commit()

    # 2. Sync Schemes from Connectors
    synced_count = 0
    connectors = connector_registry.get_all_scheme_connectors()

    for conn in connectors:
        schemes_data = conn.fetch_schemes()
        for s in schemes_data:
            existing = db.query(Scheme).filter(Scheme.code == s["code"]).first()
            if not existing:
                scheme = Scheme(
                    code=s["code"],
                    name=s["name"],
                    short_description=s["short_description"],
                    benefit_summary=s["benefit_summary"],
                    level=SchemeLevelEnum(s["level"]),
                    department=s["department"],
                    category_id=s["category_id"],
                    benefit_type=BenefitTypeEnum(s["benefit_type"]),
                    eligibility_unit=EligibilityUnitEnum(s["eligibility_unit"]),
                    target_groups=s.get("target_groups", []),
                    rules_key=s["rules_key"],
                    rule_version=s.get("rule_version", "1.0"),
                    official_url=s["official_url"],
                    require_officer_confirmation_before_apply=s.get("require_officer_confirmation_before_apply", False),
                    source_system=s.get("source_system", conn.source_system),
                    last_synced_at=datetime.utcnow(),
                    is_active=True,
                )
                db.add(scheme)
            else:
                existing.name = s["name"]
                existing.short_description = s["short_description"]
                existing.benefit_summary = s["benefit_summary"]
                existing.level = SchemeLevelEnum(s["level"])
                existing.department = s["department"]
                existing.category_id = s["category_id"]
                existing.benefit_type = BenefitTypeEnum(s["benefit_type"])
                existing.eligibility_unit = EligibilityUnitEnum(s["eligibility_unit"])
                existing.target_groups = s.get("target_groups", existing.target_groups)
                existing.official_url = s["official_url"]
                existing.require_officer_confirmation_before_apply = s.get("require_officer_confirmation_before_apply", False)
                existing.last_synced_at = datetime.utcnow()

            synced_count += 1

    db.commit()
    logger.info(f"Successfully synchronized {synced_count} schemes into master database.")
    return synced_count
