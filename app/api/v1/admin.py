from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_admin
from app.models.user import User
from app.models.audit_log import AuditLog
from app.models.case import Case
from app.models.hearing import Hearing
from app.models.document import Document

from app.schemas.admin import (
    AdminOverviewOut,
    AdminUserInspectionOut,
    AdminUserOut,
    AuditLogOut,
)

from app.services.admin_service import (
    get_admin_overview,
    inspect_user,
    set_user_active_status,
)

router = APIRouter(tags=["Admin"])


# =====================================
# Admin Overview
# =====================================
@router.get("/overview", response_model=AdminOverviewOut)
def admin_overview(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    return get_admin_overview(db)


# =====================================
# Inspect Single User
# =====================================
@router.get("/users/{user_id}", response_model=AdminUserInspectionOut)
def admin_inspect_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    data = inspect_user(db=db, user_id=user_id)

    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return data


# =====================================
# Suspend User
# =====================================
@router.post("/users/{user_id}/suspend", response_model=AdminUserOut)
def suspend_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    if user_id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Admin cannot suspend himself",
        )

    user = set_user_active_status(
        db=db,
        user_id=user_id,
        is_active=False,
        admin_id=current_admin.id,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # 🔥 calculate counts
    cases_count = db.query(Case).filter(Case.user_id == user.id).count()

    hearings_count = (
        db.query(Hearing)
        .join(Case, Hearing.case_id == Case.id)
        .filter(Case.user_id == user.id)
        .count()
    )

    documents_count = (
        db.query(Document)
        .join(Case, Document.case_id == Case.id)
        .filter(Case.user_id == user.id)
        .count()
    )

    return {
        "id": user.id,
        "phone": user.phone,
        "is_active": user.is_active,
        "is_admin": user.is_admin,
        "cases_count": cases_count,
        "hearings_count": hearings_count,
        "documents_count": documents_count,
    }


# =====================================
# Activate User
# =====================================
@router.post("/users/{user_id}/activate", response_model=AdminUserOut)
def activate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    user = set_user_active_status(
        db=db,
        user_id=user_id,
        is_active=True,
        admin_id=current_admin.id,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    cases_count = db.query(Case).filter(Case.user_id == user.id).count()

    hearings_count = (
        db.query(Hearing)
        .join(Case, Hearing.case_id == Case.id)
        .filter(Case.user_id == user.id)
        .count()
    )

    documents_count = (
        db.query(Document)
        .join(Case, Document.case_id == Case.id)
        .filter(Case.user_id == user.id)
        .count()
    )

    return {
        "id": user.id,
        "phone": user.phone,
        "is_active": user.is_active,
        "is_admin": user.is_admin,
        "cases_count": cases_count,
        "hearings_count": hearings_count,
        "documents_count": documents_count,
    }


# =====================================
# Audit Logs
# =====================================
@router.get("/audit-logs", response_model=list[AuditLogOut])
def get_audit_logs(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    logs = (
        db.query(AuditLog)
        .order_by(AuditLog.created_at.desc())
        .limit(100)
        .all()
    )

    result = []

    for log in logs:
        result.append({
            "id": log.id,
            "action": log.action,
            "description": log.description,
            "actor_user_id": log.actor_user_id,
            "target_user_id": log.target_user_id,
            "actor_phone": log.actor.phone if log.actor else None,
            "target_phone": log.target.phone if log.target else None,
            "created_at": log.created_at,
        })

    return result


# =====================================
# System Health
# =====================================
@router.get("/system-health")
def system_health(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    return {
        "status": "ok",
        "database": "connected",
        "users": db.query(User).count(),
        "cases": db.query(Case).count(),
        "hearings": db.query(Hearing).count(),
        "documents": db.query(Document).count(),
    }


# =====================================
# List All Users (WITH COUNTS)
# =====================================
@router.get("/users", response_model=list[AdminUserOut])
def list_users(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    users = db.query(User).order_by(User.id.desc()).all()

    result = []

    for user in users:
        # Count cases directly
        cases_count = db.query(Case).filter(Case.user_id == user.id).count()

        # Count hearings through cases
        hearings_count = (
            db.query(Hearing)
            .join(Case, Hearing.case_id == Case.id)
            .filter(Case.user_id == user.id)
            .count()
        )

        # Count documents through cases
        documents_count = (
            db.query(Document)
            .join(Case, Document.case_id == Case.id)
            .filter(Case.user_id == user.id)
            .count()
        )

        result.append({
            "id": user.id,
            "phone": user.phone,
            "is_active": user.is_active,
            "is_admin": user.is_admin,
            "cases_count": cases_count,
            "hearings_count": hearings_count,
            "documents_count": documents_count,
        })

    return result
