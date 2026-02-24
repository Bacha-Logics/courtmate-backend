from app.db.base import Base

# Import all models here for Alembic
from app.models.user import User
from app.models.case import Case
from app.models.hearing import Hearing
from app.models.document import Document
from app.models.reminder import Reminder
from app.models.audit_log import AuditLog

