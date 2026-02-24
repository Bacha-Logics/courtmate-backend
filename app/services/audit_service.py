from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog


def create_audit_log(
    *,
    db: Session,
    action: str,
    actor_user_id: int | None,
    target_user_id: int | None = None,
    description: str | None = None,
):
    log = AuditLog(
        action=action,
        actor_user_id=actor_user_id,
        target_user_id=target_user_id,
        description=description,
    )

    db.add(log)
    db.commit()
