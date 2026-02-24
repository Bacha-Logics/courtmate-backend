from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.reminder import Reminder
from app.models.hearing import Hearing
from app.models.user import User


def create_reminders_for_hearing(
    *,
    db: Session,
    hearing: Hearing,
    current_user: User,
):
    reminders = []

    hearing_datetime = datetime.combine(
        hearing.hearing_date,
        hearing.hearing_time
    )

    # 1 Day Before
    one_day_before = hearing_datetime - timedelta(days=1)
    reminders.append(
        Reminder(
            type="1_day_before",
            remind_at=one_day_before,
            hearing_id=hearing.id,
            user_id=current_user.id,
        )
    )

    # 2 Hours Before
    two_hours_before = hearing_datetime - timedelta(hours=2)
    reminders.append(
        Reminder(
            type="2_hours_before",
            remind_at=two_hours_before,
            hearing_id=hearing.id,
            user_id=current_user.id,
        )
    )

    # After Hearing (30 minutes after end)
    after_hearing = hearing_datetime + timedelta(minutes=30)
    reminders.append(
        Reminder(
            type="after_hearing",
            remind_at=after_hearing,
            hearing_id=hearing.id,
            user_id=current_user.id,
        )
    )

    db.add_all(reminders)
    db.commit()

    return reminders
