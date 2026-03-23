from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class Progress(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    user_id: str
    subject: str
    answered_ids: List[str] = []
    incorrect_ids: List[str] = []
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True


class ProgressUpdate(BaseModel):
    answered_ids: List[str]
    incorrect_ids: List[str]


class ProgressPublic(BaseModel):
    subject: str
    answered_ids: List[str]
    incorrect_ids: List[str]
    updated_at: datetime
