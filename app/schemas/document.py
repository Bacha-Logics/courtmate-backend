from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class DocumentOut(BaseModel):
    id: int
    original_name: str
    file_type: str
    file_size: int
    uploaded_at: datetime
    case_id: int

    class Config:
        from_attributes = True
