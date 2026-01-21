from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class NoteBase(BaseModel):
    title: str
    tags: Optional[str] = None
    created_by: str

class NoteCreate(NoteBase):
    pass

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    tags: Optional[str] = None
    created_by: Optional[str] = None

class Note(NoteBase):
    id: int
    created_at: datetime
    last_accessed_at: datetime
    deleted_at: Optional[datetime] = None # Add this line!

    class Config:
        from_attributes = True