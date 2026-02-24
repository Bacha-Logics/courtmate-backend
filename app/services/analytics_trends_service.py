from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.case import Case, CaseStatus
from app.models.hearing import Hearing
from app.models.user import User


def get_analytics_trends(
    db: Session,
    current_user: User,
):
    """
    Analytics Trends API

    Purpose:
    - Show time-based activity trends for a lawyer
    - This is NOT a snapshot (dashboard)
    - This is historical flow data used for charts and insights

    Returns:
    - hearings_weekly: number of hearings per week (last 6 weeks)
    - cases_monthly: opened vs closed cases per month + velocity
    """

    today = date.today()

    # ============================================================
    # HEARINGS TREND (Last 6 Weeks)
    # ------------------------------------------------------------
    # Question answered:
    # "How busy was I in court week by week?"
    #
    # We group hearings by week using hearing_date
    # and count how many hearings happened in each week.
    # ============================================================
    six_weeks_ago = today - timedelta(weeks=6)

    weekly_hearings = (
        db.query(
            func.date_trunc("week", Hearing.hearing_date).label("week"),
            func.count(Hearing.id).label("count"),
        )
        .join(Case)  # join to enforce ownership via Case.user_id
        .filter(
            Case.user_id == current_user.id,
            Hearing.hearing_date >= six_weeks_ago,
        )
        .group_by("week")
        .order_by("week")
        .all()
    )

    # Format weekly hearings for API response
    hearings_weekly = [
        {
            "week_start": row.week.date().isoformat(),
            "count": row.count,  # number of hearings in that week
        }
        for row in weekly_hearings
    ]

    # ============================================================
    # CASES TREND (Last 6 Months)
    # ------------------------------------------------------------
    # Question answered:
    # "How many cases am I opening vs closing over time?"
    #
    # This is FLOW data, not state.
    # ============================================================
    start_month = today.replace(day=1) - timedelta(days=180)

    # ------------------------------------------------------------
    # OPENED CASES
    # ------------------------------------------------------------
    # A case is considered "opened" in the month it was CREATED.
    # Based purely on created_at.
    # ------------------------------------------------------------
    opened_cases = (
        db.query(
            func.date_trunc("month", Case.created_at).label("month"),
            func.count(Case.id).label("count"),
        )
        .filter(
            Case.user_id == current_user.id,
            Case.created_at >= start_month,
        )
        .group_by("month")
        .order_by("month")
        .all()
    )

    # ------------------------------------------------------------
    # CLOSED CASES
    # ------------------------------------------------------------
    # A case is considered "closed" in the month it was CLOSED.
    # This is why closed_at is critical.
    # ------------------------------------------------------------
    closed_cases = (
        db.query(
            func.date_trunc("month", Case.closed_at).label("month"),
            func.count(Case.id).label("count"),
        )
        .filter(
            Case.user_id == current_user.id,
            Case.status == CaseStatus.closed,
            Case.closed_at.isnot(None),
            Case.closed_at >= start_month,
        )
        .group_by("month")
        .order_by("month")
        .all()
    )

    # Map closed counts by month for quick lookup
    closed_map = {
        row.month.strftime("%Y-%m"): row.count
        for row in closed_cases
    }

    # ============================================================
    # FINAL MONTHLY TREND PAYLOAD
    # ------------------------------------------------------------
    # For each month:
    # - opened  = cases created
    # - closed  = cases closed
    # - velocity = closed - opened
    #
    # Velocity meaning:
    # - 0   → workload stable
    # - <0  → backlog increasing
    # - >0  → backlog shrinking
    # ============================================================
    cases_monthly = []

    for row in opened_cases:
        month_key = row.month.strftime("%Y-%m")
        opened = row.count
        closed = closed_map.get(month_key, 0)

        cases_monthly.append({
            "month": month_key,
            "opened": opened,
            "closed": closed,
            "velocity": closed - opened,  # core productivity signal
        })

    # ============================================================
    # FINAL RESPONSE
    # ============================================================
    return {
        "hearings_weekly": hearings_weekly,
        "cases_monthly": cases_monthly,
    }
