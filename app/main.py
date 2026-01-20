import uuid
from fastapi import FastAPI, Request, HTTPException, Security, status, Depends
from fastapi.security import APIKeyHeader
from middleware.CorrelationMiddleware import CorrelationIdMiddleware 
from middleware.PerformanceMonitorMiddleware import PerformanceMonitorMiddleware
from sqlalchemy.orm import Session
from . import models, schemas, database
from typing import List
from middleware.access_logging import SecretAccessMiddleware


models.Base.metadata.create_all(bind=database.engine)
app = FastAPI(title="Basic-CRUD-APP")



# Dependency to get DB session
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()
          
app.add_middleware(CorrelationIdMiddleware)        
app.add_middleware(PerformanceMonitorMiddleware)
app.add_middleware(SecretAccessMiddleware)

API_KEY_NAME = "access_token"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

def validate_api_key(api_key: str = Security(api_key_header)):
    if api_key != "cp-secure-key-2026":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Unauthorized Access"
        )
    return True

@app.get("/health")
async def health_check():
    return {"status": "online", "gateway_version": "1.0.SASE"}

from pydantic import BaseModel

@app.post("/notes", response_model=schemas.Note)
def create_note(note: schemas.NoteCreate, db: Session = Depends(get_db)):
    db_note = models.Note(**note.dict())
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

@app.get("/notes", response_model=List[schemas.Note])
def list_notes(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(models.Note).offset(skip).limit(limit).all()

@app.get("/notes/{note_id}", response_model=schemas.Note)
def read_note(note_id: int, db: Session = Depends(get_db)):
    note = db.query(models.Note).filter(models.Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    # Update last_accessed_at logic here if desired
    return note

@app.delete("/notes/{note_id}")
def delete_note(note_id: int, db: Session = Depends(get_db)):
    note = db.query(models.Note).filter(models.Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(note)
    db.commit()
    return {"message": "Deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)