from sqlalchemy.orm import Session
from sqlalchemy import func, case

from app.models.case import Case
from app.models.user import User


def get_clients(db: Session, current_user: User):
    """
    Returns distinct clients derived from cases
    Includes total cases and active cases
    """

    rows = (
        db.query(
            Case.client_name,
            Case.client_phone,
            func.count(Case.id).label("total_cases"),
            func.sum(
                case(
                    (Case.status == "active", 1),
                    else_=0
                )
            ).label("active_cases")
        )
        .filter(
            Case.user_id == current_user.id,
            Case.client_phone.isnot(None)
        )
        .group_by(Case.client_name, Case.client_phone)
        .order_by(func.count(Case.id).desc())
        .all()
    )

    return [
        {
            "client_name": r.client_name,
            "client_phone": r.client_phone,
            "total_cases": r.total_cases,
            "active_cases": int(r.active_cases or 0),
        }
        for r in rows
    ]


def get_client_cases(
    db: Session,
    current_user: User,
    client_phone: str
):
    return (
        db.query(Case)
        .filter(
            Case.user_id == current_user.id,
            Case.client_phone == client_phone
        )
        .all()
    )
