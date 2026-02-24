from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct

from app.models.case import Case, CaseStatus
from app.models.hearing import Hearing
from app.models.user import User


def get_dashboard_data(db: Session, current_user: User):
    today = date.today()
    tomorrow = today + timedelta(days=1)
    upcoming_end = today + timedelta(days=7)

    # -------------------------
    # Hearings
    # -------------------------

    today_hearings = (
        db.query(Hearing)
        .join(Case)
        .filter(
            Case.user_id == current_user.id,
            Hearing.hearing_date == today
        )
        .all()
    )

    tomorrow_hearings = (
        db.query(Hearing)
        .join(Case)
        .filter(
            Case.user_id == current_user.id,
            Hearing.hearing_date == tomorrow
        )
        .all()
    )

    upcoming_hearings = (
        db.query(Hearing)
        .join(Case)
        .filter(
            Case.user_id == current_user.id,
            Hearing.hearing_date > tomorrow,
            Hearing.hearing_date <= upcoming_end
        )
        .all()
    )

    # -------------------------
    # Case Counts (FIXED LOGIC)
    # -------------------------

    total_cases = (
        db.query(func.count(Case.id))
        .filter(Case.user_id == current_user.id)
        .scalar()
    )

    # ✅ FIXED: Count ONLY active cases
    active_cases = (
        db.query(func.count(Case.id))
        .filter(
            Case.user_id == current_user.id,
            Case.status == CaseStatus.active
        )
        .scalar()
    )

    # -------------------------
    # Hearing Count (REAL TOTAL)
    # -------------------------

    total_hearings = (
        db.query(func.count(Hearing.id))
        .join(Case)
        .filter(Case.user_id == current_user.id)
        .scalar()
    )

    # -------------------------
    # Clients Count
    # -------------------------

    total_clients = (
        db.query(func.count(distinct(Case.client_phone)))
        .filter(
            Case.user_id == current_user.id,
            Case.client_phone.isnot(None)
        )
        .scalar()
    )

    return {
        "today_hearings": today_hearings,
        "upcoming_hearings": upcoming_hearings,
        "counts": {
            "active_cases": active_cases or 0,
            "total_cases": total_cases or 0,
            "total_hearings": total_hearings or 0,
            "today_hearings": len(today_hearings),
            "upcoming_hearings": len(upcoming_hearings),
            "total_clients": total_clients or 0,
        }
    }