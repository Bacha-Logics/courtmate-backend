from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.schemas.dashboard import DashboardOut
from app.services.dashboard_service import get_dashboard_data
from app.models.user import User

router = APIRouter(tags=["Dashboard"])


@router.get(
    "",
    response_model=DashboardOut,
    summary="Get dashboard overview"
)
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_dashboard_data(
        db=db,
        current_user=current_user
    )
