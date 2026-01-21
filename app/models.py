from sqlalchemy import Column, Integer, String, DateTime, event
from datetime import datetime
from .database import Base
from sqlalchemy.sql import func

class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    tags = Column(String)  # Stored as comma-separated string
    created_by = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_accessed_at = Column(DateTime, default=datetime.utcnow, onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True) # If this is null, the note is "active"
    
@event.listens_for(Note, 'load')
def receive_load(target, context):
    # This triggers whenever a Note is pulled from the DB
    target.last_accessed_at = datetime.utcnow()