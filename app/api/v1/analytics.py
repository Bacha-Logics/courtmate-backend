from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.analytics_trends import AnalyticsTrendsOut
from app.services.analytics_trends_service import get_analytics_trends

from app.api.deps import get_db, get_current_user
from app.schemas.analytics import AnalyticsSummaryOut
from app.services.analytics_service import get_analytics_summary
from app.models.user import User

router = APIRouter(

    tags=["Analytics"]
)


@router.get(
    "/summary",
    response_model=AnalyticsSummaryOut
)
def analytics_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Advanced analytics summary for lawyers
    """
    return get_analytics_summary(db, current_user)


@router.get(
    "/trends",
    response_model=AnalyticsTrendsOut
)
def analytics_trends(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_analytics_trends(
        db=db,
        current_user=current_user,
    )