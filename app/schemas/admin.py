from pydantic import BaseModel
from typing import List
from datetime import datetime
from app.schemas.case import CaseOut
from app.schemas.hearing import HearingOut
from app.schemas.document import DocumentOut


class AdminOverviewOut(BaseModel):
    total_users: int
    total_cases: int
    total_hearings: int
    total_documents: int


class AdminUserOut(BaseModel):
    id: int
    phone: str
    is_active: bool
    is_admin: bool

    # ✅ NEW — per-user statistics
    cases_count: int
    hearings_count: int
    documents_count: int

    class Config:
        from_attributes = True


class AdminUserInspectionOut(BaseModel):
    user: AdminUserOut
    cases: List[CaseOut]
    hearings: List[HearingOut]
    documents: List[DocumentOut]


class AuditLogOut(BaseModel):
    id: int
    action: str
    description: str | None
    actor_user_id: int | None
    target_user_id: int | None

    # ✅ NEW — show phones in logs
    actor_phone: str | None
    target_phone: str | None

    created_at: datetime

    class Config:
        from_attributes = True
