from datetime import datetime
from pydantic import BaseModel


class ReminderOut(BaseModel):
    id: int
    hearing_id: int
    user_id: int
    type: str
    remind_at: datetime
    is_sent: bool
    sent_at: datetime | None = None
    retry_count: int
    max_retries: int
    created_at: datetime

    class Config:
        from_attributes = True
