from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_db, get_current_user
from app.schemas.hearing import HearingCreate, HearingOut
from app.services import hearing_service
from app.models.user import User

router = APIRouter(tags=["Hearings"])


# -------------------------
# Add Hearing
# -------------------------
@router.post(
    "",
    response_model=HearingOut,
    status_code=status.HTTP_201_CREATED
)
def add_hearing(
    hearing_in: HearingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    hearing = hearing_service.create_hearing(
        db=db,
        hearing_in=hearing_in,
        current_user=current_user
    )

    if not hearing:
        raise HTTPException(
            status_code=404,
            detail="Case not found"
        )

    return hearing


# -------------------------
# Today's Hearings
# -------------------------
@router.get(
    "/today",
    response_model=List[HearingOut]
)
def today_hearings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return hearing_service.get_today_hearings(
        db=db,
        current_user=current_user
    )


# -------------------------
# Tomorrow's Hearings
# -------------------------
@router.get(
    "/tomorrow",
    response_model=List[HearingOut]
)
def tomorrow_hearings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return hearing_service.get_tomorrow_hearings(
        db=db,
        current_user=current_user
    )


# -------------------------
# Upcoming Hearings (7 days)
# -------------------------
@router.get(
    "/upcoming",
    response_model=List[HearingOut]
)
def upcoming_hearings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return hearing_service.get_upcoming_hearings(
        db=db,
        current_user=current_user
    )
