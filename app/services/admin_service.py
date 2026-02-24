from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.user import User
from app.models.case import Case
from app.models.hearing import Hearing
from app.models.document import Document
from app.services.audit_service import create_audit_log


def get_admin_overview(db: Session):
    """
    System-wide admin overview counts
    """

    return {
        "total_users": db.query(func.count(User.id)).scalar() or 0,
        "total_cases": db.query(func.count(Case.id)).scalar() or 0,
        "total_hearings": db.query(func.count(Hearing.id)).scalar() or 0,
        "total_documents": db.query(func.count(Document.id)).scalar() or 0,
    }


def inspect_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None

    # Fetch related data
    cases = db.query(Case).filter(Case.user_id == user.id).all()

    hearings = (
        db.query(Hearing)
        .join(Case, Hearing.case_id == Case.id)
        .filter(Case.user_id == user.id)
        .all()
    )

    documents = (
        db.query(Document)
        .filter(Document.user_id == user.id)
        .all()
    )

    # 🔥 Calculate counts
    cases_count = len(cases)
    hearings_count = len(hearings)
    documents_count = len(documents)

    return {
        "user": {
            "id": user.id,
            "phone": user.phone,
            "is_active": user.is_active,
            "is_admin": user.is_admin,
            "cases_count": cases_count,
            "hearings_count": hearings_count,
            "documents_count": documents_count,
        },
        "cases": cases,
        "hearings": hearings,
        "documents": documents,
    }

def set_user_active_status(
    db: Session,
    user_id: int,
    is_active: bool,
    admin_id: int,
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None

    user.is_active = is_active
    db.commit()

    create_audit_log(
        db=db,
        action="ACTIVATE_USER" if is_active else "SUSPEND_USER",
        actor_user_id=admin_id,
        target_user_id=user.id,
        description=f"User {'activated' if is_active else 'suspended'} by admin"
    )

    return user
