from sqlalchemy.orm import joinedload
from datetime import date, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.hearing import Hearing
from app.models.case import Case, CaseStatus
from app.models.user import User
from app.schemas.hearing import HearingCreate
from app.services.reminder_service import create_reminders_for_hearing


# -------------------------
# Create Hearing
# -------------------------
def create_hearing(
    db: Session,
    hearing_in: HearingCreate,
    current_user: User,
):
    # 1️⃣ Validate case ownership
    case = (
        db.query(Case)
        .filter(
            Case.id == hearing_in.case_id,
            Case.user_id == current_user.id
        )
        .first()
    )

    if not case:
        return None

    # 🚫 Block closed cases
    if case.status == CaseStatus.closed:
        raise HTTPException(
            status_code=400,
            detail="Cannot add hearing to a closed case"
        )

    # ✅ Auto-activate case
    if case.status == CaseStatus.pending:
        case.status = CaseStatus.active

    # 2️⃣ Create hearing
    hearing = Hearing(
        hearing_date=hearing_in.hearing_date,
        hearing_time=hearing_in.hearing_time,
        notes=hearing_in.notes,
        case_id=case.id
    )

    db.add(hearing)
    db.commit()
    db.refresh(hearing)

    # 3️⃣ Create automatic reminders
    create_reminders_for_hearing(
        db=db,
        hearing=hearing,
        current_user=current_user
    )

    return hearing


# -------------------------
# Today's Hearings
# -------------------------
def get_today_hearings(
    db: Session,
    current_user: User
):
    today = date.today()

    return (
        db.query(Hearing)
        .options(joinedload(Hearing.case))   # 🔥 important
        .join(Case)
        .filter(
            Case.user_id == current_user.id,
            Hearing.hearing_date == today
        )
        .order_by(Hearing.hearing_time)
        .all()
    )


# -------------------------
# Tomorrow's Hearings
# -------------------------
def get_tomorrow_hearings(
    db: Session,
    current_user: User
):
    tomorrow = date.today() + timedelta(days=1)

    return (
        db.query(Hearing)
        .options(joinedload(Hearing.case))
        .join(Case)
        .filter(
            Case.user_id == current_user.id,
            Hearing.hearing_date == tomorrow
        )
        .order_by(Hearing.hearing_time)
        .all()
    )


# -------------------------
# Upcoming Hearings (Next 7 Days - AFTER tomorrow)
# -------------------------
def get_upcoming_hearings(
    db: Session,
    current_user: User
):
    today = date.today()
    tomorrow = today + timedelta(days=1)
    upcoming_end = today + timedelta(days=7)

    return (
        db.query(Hearing)
        .options(joinedload(Hearing.case))
        .join(Case)
        .filter(
            Case.user_id == current_user.id,
            Hearing.hearing_date > tomorrow,
            Hearing.hearing_date <= upcoming_end
        )
        .order_by(Hearing.hearing_date, Hearing.hearing_time)
        .all()
    )
