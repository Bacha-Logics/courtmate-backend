from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.case import Case, CaseStatus
from app.models.hearing import Hearing
from app.models.user import User


def get_analytics_summary(
    db: Session,
    current_user: User,
):
    today = date.today()
    last_7_days = today - timedelta(days=7)
    next_7_days = today + timedelta(days=7)

    total_cases = (
        db.query(Case)
        .filter(Case.user_id == current_user.id)
        .count()
    )

    active_cases = (
        db.query(Case)
        .filter(
            Case.user_id == current_user.id,
            Case.status == CaseStatus.active
        )
        .count()
    )

    pending_cases = (
    db.query(func.count(Case.id))
    .filter(
        Case.user_id == current_user.id,
        Case.status == CaseStatus.pending
    )
    .scalar()
    or 0
    )



    closed_cases = (
        db.query(Case)
        .filter(
            Case.user_id == current_user.id,
            Case.status == CaseStatus.closed
        )
        .count()
    )

    hearings_last_7_days = (
        db.query(Hearing)
        .join(Case)
        .filter(
            Case.user_id == current_user.id,
            Hearing.hearing_date >= last_7_days,
            Hearing.hearing_date <= today
        )
        .count()
    )

    hearings_next_7_days = (
        db.query(Hearing)
        .join(Case)
        .filter(
            Case.user_id == current_user.id,
            Hearing.hearing_date > today,
            Hearing.hearing_date <= next_7_days
        )
        .count()
    )

    return {
        "total_cases": total_cases,
        "active_cases": active_cases,
        "pending": pending_cases,
        "closed_cases": closed_cases,
        "hearings_last_7_days": hearings_last_7_days,
        "hearings_next_7_days": hearings_next_7_days,
    }
