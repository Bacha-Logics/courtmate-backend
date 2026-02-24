from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)

    # Original file name uploaded by user
    original_name = Column(String, nullable=False)

    # Internal stored file name (UUID / hash)
    stored_name = Column(String, nullable=False, unique=True)

    file_type = Column(String, nullable=False)   # pdf / image
    file_size = Column(Integer, nullable=False)  # bytes

    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    case_id = Column(
        Integer,
        ForeignKey("cases.id", ondelete="CASCADE"),
        nullable=False
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    # Relationships
    case = relationship("Case", back_populates="documents")
    user = relationship("User", back_populates="documents")
