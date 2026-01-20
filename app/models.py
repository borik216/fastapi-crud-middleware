from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from .database import Base

class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    tags = Column(String)  # Stored as comma-separated string
    created_by = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_accessed_at = Column(DateTime, default=datetime.utcnow)