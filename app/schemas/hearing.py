from pydantic import BaseModel
from datetime import date, time
from typing import Optional


# ---------------------------------
# Case Basic Schema (nested)
# ---------------------------------
class CaseBasic(BaseModel):
    id: int
    title: str
    case_number: str
    court_name: Optional[str] = None   # 🔥 added

    class Config:
        from_attributes = True


# ---------------------------------
# Shared fields
# ---------------------------------
class HearingBase(BaseModel):
    hearing_date: Optional[date] = None
    hearing_time: Optional[time] = None
    notes: Optional[str] = None


# ---------------------------------
# Create hearing
# ---------------------------------
class HearingCreate(HearingBase):
    case_id: int
    hearing_date: date


# ---------------------------------
# Response schema
# ---------------------------------
class HearingOut(HearingBase):
    id: int
    hearing_date: date
    case: CaseBasic   # 🔥 nested full case preview

    class Config:
        from_attributes = True