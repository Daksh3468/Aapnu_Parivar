from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.audit import AuditLog


def write_audit(
    db: Session,
    actor_user_id: Optional[str],
    actor_role: str,
    action: str,
    entity_type: str,
    entity_id: Optional[str] = None,
    family_id: Optional[str] = None,
    purpose: Optional[str] = None,
    ip_address: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
) -> AuditLog:
    """Record an immutable append-only audit entry."""
    audit = AuditLog(
        actor_user_id=actor_user_id,
        actor_role=actor_role,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        family_id=family_id,
        purpose=purpose,
        ip_address=ip_address,
        details=details,
    )
    db.add(audit)
    db.commit()
    db.refresh(audit)
    return audit
