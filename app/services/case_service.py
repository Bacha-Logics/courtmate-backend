from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List, Optional
from datetime import datetime, timezone
from app.models.case import Case, CaseStatus
from app.schemas.case import CaseCreate, CaseUpdate
from app.models.user import User


# -------------------------
# Create a new case
# -------------------------
def create_case(
    db: Session,
    *,
    case_in: CaseCreate,
    current_user: User
) -> Case:
    case = Case(
        title=case_in.title,
        case_number=case_in.case_number,
        court_type=case_in.court_type,
        court_name=case_in.court_name,
        judge_name=case_in.judge_name,
        client_name=case_in.client_name,
        client_phone=case_in.client_phone,
        opponent_name=case_in.opponent_name,
        status=CaseStatus.pending,  # 🔒 ALWAYS pending
        user_id=current_user.id,
    )

    db.add(case)
    db.commit()
    db.refresh(case)
    return case


# -------------------------
# Get all cases for current user
# -------------------------
def get_user_cases(
    db: Session,
    *,
    current_user: User
) -> List[Case]:
    return (
        db.query(Case)
        .filter(Case.user_id == current_user.id)
        .order_by(Case.id.desc())
        .all()
    )


# -------------------------
# Get a single case by ID
# -------------------------
def get_case_by_id(
    db: Session,
    *,
    case_id: int,
    current_user: User
) -> Optional[Case]:
    return (
        db.query(Case)
        .filter(
            Case.id == case_id,
            Case.user_id == current_user.id
        )
        .first()
    )


# -------------------------
# Update case
# -------------------------
def update_case(
    db: Session,
    *,
    db_case: Case,
    case_in: CaseUpdate
) -> Case:
    update_data = case_in.model_dump(exclude_unset=True)

    # =========================
    # Status transition guards
    # =========================
    if "status" in update_data:
        new_status = update_data["status"]

        # ❌ Closed means final
        if db_case.status == CaseStatus.closed:
            raise HTTPException(
                status_code=400,
                detail="Closed cases cannot be reopened"
            )

        # ❌ Pending → Closed is not allowed
        if (
            db_case.status == CaseStatus.pending
            and new_status == CaseStatus.closed
        ):
            raise HTTPException(
                status_code=400,
                detail="Pending cases must become active before closing"
            )

        # ✅ Active → Closed (wire closed_at)
        if (
            db_case.status == CaseStatus.active
            and new_status == CaseStatus.closed
        ):
            db_case.closed_at = datetime.now(timezone.utc)

    # =========================
    # Apply updates
    # =========================
    for field, value in update_data.items():
        setattr(db_case, field, value)

    db.add(db_case)
    db.commit()
    db.refresh(db_case)
    return db_case

# -------------------------
# Delete case
# -------------------------
def delete_case(
    db: Session,
    *,
    db_case: Case
) -> None:
    db.delete(db_case)
    db.commit()
