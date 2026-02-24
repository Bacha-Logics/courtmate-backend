from app.models.user import User
from app.models.case import Case
from app.models.hearing import Hearing

APP_LOGIN_URL = "https://yourdomain.com/login"


def build_message(reminder_type: str, case: Case, hearing: Hearing) -> str:

    base = (
        f"Case: {case.title}\n"
        f"Case No: {case.case_number}\n"
        f"Court: {case.court_name}\n"
        f"Date: {hearing.hearing_date}\n"
        f"Time: {hearing.hearing_time}\n\n"
    )

    if reminder_type == "1_day_before":
        return "Reminder: Your hearing is tomorrow.\n\n" + base

    if reminder_type == "2_hours_before":
        return "Reminder: Your hearing starts in 2 hours.\n\n" + base

    if reminder_type == "after_hearing":
        return (
            "Hearing Completed.\n\n"
            + base +
            f"Add next hearing here:\n{APP_LOGIN_URL}"
        )

    return base


def send_whatsapp_message(*, user: User, case: Case, hearing: Hearing, reminder_type: str) -> bool:
    try:
        message = build_message(reminder_type, case, hearing)
        print(f"[WHATSAPP → {user.phone}] {message}")
        return True
    except Exception as e:
        print("WhatsApp error:", e)
        return False


def send_sms_message(*, user: User, case: Case, hearing: Hearing, reminder_type: str) -> bool:
    try:
        message = build_message(reminder_type, case, hearing)
        print(f"[SMS → {user.phone}] {message}")
        return True
    except Exception as e:
        print("SMS error:", e)
        return False
