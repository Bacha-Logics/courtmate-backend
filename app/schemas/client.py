from pydantic import BaseModel
from typing import Optional


class ClientOut(BaseModel):
    client_name: Optional[str]
    client_phone: Optional[str]
    total_cases: int
    active_cases: int   # ✅ ADDED

    class Config:
        from_attributes = True
