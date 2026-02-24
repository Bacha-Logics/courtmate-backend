from pydantic import BaseModel
from typing import List, Optional

from app.schemas.case import CaseOut
from app.schemas.hearing import HearingOut


class CaseDetailOut(BaseModel):
    case: CaseOut
    hearings: List[HearingOut]
    next_hearing: Optional[HearingOut] = None

    class Config:
        from_attributes = True
