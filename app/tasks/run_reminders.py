from app.db.base_class import * 
from app.db.session import SessionLocal
from app.services.reminder_delivery import process_due_reminders


def run():
    db = SessionLocal()
    try:
        count = process_due_reminders(db)
        print(f"[INFO] {count} reminder(s) processed.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
