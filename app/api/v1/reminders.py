from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.reminder import Reminder
from app.models.user import User
from app.schemas.reminder import ReminderOut  # make sure this exists

router = APIRouter(tags=["Reminders"])


# ============================================================
# GET ALL REMINDERS (with filtering)
# ============================================================
@router.get("", response_model=List[ReminderOut])
def get_reminders(
    status: Optional[str] = None,  # pending | sent | failed
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Fetch reminders for logged-in user.

    Optional Filters:
    - status=pending
    - status=sent
    - status=failed
    """

    query = db.query(Reminder).filter(
        Reminder.user_id == current_user.id
    )

    if status == "pending":
        query = query.filter(Reminder.is_sent.is_(False))

    elif status == "sent":
        query = query.filter(Reminder.is_sent.is_(True))

    elif status == "failed":
        query = query.filter(
            Reminder.is_sent.is_(False),
            Reminder.retry_count >= Reminder.max_retries
        )

    reminders = query.order_by(Reminder.remind_at.desc()).all()

    return reminders


# ============================================================
# GET SINGLE REMINDER
# ============================================================
@router.get("/{reminder_id}", response_model=ReminderOut)
def get_single_reminder(
    reminder_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reminder = db.query(Reminder).filter(
        Reminder.id == reminder_id,
        Reminder.user_id == current_user.id
    ).first()

    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found"
        )

    return reminder


# ============================================================
# DELETE REMINDER
# ============================================================
@router.delete("/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reminder(
    reminder_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reminder = db.query(Reminder).filter(
        Reminder.id == reminder_id,
        Reminder.user_id == current_user.id
    ).first()

    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found"
        )

    db.delete(reminder)
    db.commit()

    return None
