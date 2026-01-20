from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class NoteBase(BaseModel):
    title: str
    tags: Optional[str] = None
    created_by: str

class NoteCreate(NoteBase):
    pass

class Note(NoteBase):
    id: int
    created_at: datetime
    last_accessed_at: datetime

    class Config:
        from_attributes = True