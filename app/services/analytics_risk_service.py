from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.case import Case, CaseStatus
from app.models.hearing import Hearing
from app.models.user import User


def get_backlog_risk(
    db: Session,
    current_user: User,
    days_without_hearing: int = 30,
):
    """
    Detect cases that are active but have gone quiet.

    A case is considered 'at risk' if:
    - status is ACTIVE
    - no hearing in the last N days
    - no upcoming hearing scheduled
    """

    today = date.today()
    cutoff_date = today - timedelta(days=days_without_hearing)

    # Subquery: last hearing date per case
    last_hearing_subq = (
        db.query(
            Hearing.case_id,
            func.max(Hearing.hearing_date).label("last_hearing_date"),
        )
        .group_by(Hearing.case_id)
        .subquery()
    )

    # Main query: active cases with old/no hearings
    risky_cases = (
        db.query(
            Case.id,
            Case.title,
            Case.case_number,
            last_hearing_subq.c.last_hearing_date,
        )
        .outerjoin(
            last_hearing_subq,
            Case.id == last_hearing_subq.c.case_id,
        )
        .filter(
            Case.user_id == current_user.id,
            Case.status == CaseStatus.active,
            (
                (last_hearing_subq.c.last_hearing_date == None) |
                (last_hearing_subq.c.last_hearing_date < cutoff_date)
            ),
        )
        .order_by(last_hearing_subq.c.last_hearing_date.asc().nullsfirst())
        .all()
    )

    return {
        "threshold_days": days_without_hearing,
        "risk_count": len(risky_cases),
        "cases": [
            {
                "case_id": row.id,
                "title": row.title,
                "case_number": row.case_number,
                "last_hearing_date": (
                    row.last_hearing_date.isoformat()
                    if row.last_hearing_date
                    else None
                ),
            }
            for row in risky_cases
        ],
    }
