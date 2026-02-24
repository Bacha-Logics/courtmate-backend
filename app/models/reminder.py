from sqlalchemy import Column, Integer, DateTime, Boolean, ForeignKey, String, func
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)

    hearing_id = Column(Integer, ForeignKey("hearings.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))

    # Reminder type
    type = Column(String, nullable=False)

    remind_at = Column(DateTime(timezone=True), nullable=False)

    is_sent = Column(Boolean, default=False)
    sent_at = Column(DateTime(timezone=True), nullable=True)

    # Retry handling
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)

    # ✅ FIXED VERSION
    created_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,      # Python-side default
        server_default=func.now(),    # DB-side default
        nullable=False                # Prevent NULL
    )

    hearing = relationship("Hearing")
    user = relationship("User")