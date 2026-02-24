from pydantic import BaseModel
from typing import List
from app.schemas.hearing import HearingOut


class DashboardCounts(BaseModel):
    active_cases: int
    total_cases: int
    total_hearings: int
    today_hearings: int
    upcoming_hearings: int
    total_clients: int


class DashboardOut(BaseModel):
    today_hearings: List[HearingOut]
    upcoming_hearings: List[HearingOut]
    counts: DashboardCounts
