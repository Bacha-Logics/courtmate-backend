from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
import enum

from app.db.base import Base


# -------------------------
# Case Status Enum
# -------------------------
class CaseStatus(str, enum.Enum):
    pending = "pending"
    active = "active"
    closed = "closed"


class Case(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String, nullable=False)
    case_number = Column(String, nullable=True)

    court_type = Column(String, nullable=True)
    court_name = Column(String, nullable=True)
    judge_name = Column(String, nullable=True)

    client_name = Column(String, nullable=True)
    client_phone = Column(String, nullable=True)
    opponent_name = Column(String, nullable=True)

    # ENUM-based status
    status = Column(
        Enum(CaseStatus, name="case_status_enum"),
        nullable=False,
        default=CaseStatus.pending
    )

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    # ✅ NEW: closure timestamp (analytics backbone)
    closed_at = Column(
        DateTime,
        nullable=True
    )

    # Relationships
    user = relationship("User", back_populates="cases")

    hearings = relationship(
        "Hearing",
        back_populates="case",
        cascade="all, delete-orphan"
    )

    documents = relationship(
        "Document",
        back_populates="case",
        cascade="all, delete-orphan"
    )
