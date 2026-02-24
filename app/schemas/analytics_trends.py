from pydantic import BaseModel
from typing import List


class WeeklyTrend(BaseModel):
    week_start: str
    count: int


class MonthlyTrend(BaseModel):
    month: str
    opened: int
    closed: int
    velocity: int


class AnalyticsTrendsOut(BaseModel):
    hearings_weekly: List[WeeklyTrend]
    cases_monthly: List[MonthlyTrend]
