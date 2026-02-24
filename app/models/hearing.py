from sqlalchemy import Column, Integer, Date, Time, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.base import Base


class Hearing(Base):
    __tablename__ = "hearings"

    id = Column(Integer, primary_key=True, index=True)
    hearing_date = Column(Date, nullable=False)
    hearing_time = Column(Time, nullable=True)
    notes = Column(Text, nullable=True)

    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False)

    case = relationship("Case", back_populates="hearings")

    reminders = relationship("Reminder", back_populates="hearing", cascade="all, delete-orphan")

