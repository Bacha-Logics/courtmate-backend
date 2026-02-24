from datetime import datetime
from sqlalchemy.orm import Session
from app.models.reminder import Reminder
from app.services.notification_service import (
    send_whatsapp_message,
    send_sms_message,
)


def process_due_reminders(db: Session) -> int:
    now = datetime.utcnow()

    reminders = (
        db.query(Reminder)
        .filter(
            Reminder.is_sent.is_(False),
            Reminder.remind_at <= now,
            Reminder.retry_count < Reminder.max_retries
        )
        .order_by(Reminder.remind_at)
        .all()
    )

    processed = 0

    for reminder in reminders:
        hearing = reminder.hearing
        case = hearing.case if hearing else None
        user = reminder.user

        if not hearing or not case or not user:
            reminder.is_sent = True
            continue

        sent = send_whatsapp_message(
            user=user,
            case=case,
            hearing=hearing,
            reminder_type=reminder.type,
        )

        if not sent:
            sent = send_sms_message(
                user=user,
                case=case,
                hearing=hearing,
                reminder_type=reminder.type,
            )

        if sent:
            reminder.is_sent = True
            reminder.sent_at = now
        else:
            reminder.retry_count += 1

        processed += 1

    db.commit()
    return processed
