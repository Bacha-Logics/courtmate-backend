from pydantic import BaseModel


class AnalyticsSummaryOut(BaseModel):
    total_cases: int
    active_cases: int
    pending: int
    closed_cases: int
    hearings_last_7_days: int
    hearings_next_7_days: int
