from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app import models, schemas
from app.api.deps.db import get_db # Assuming you moved your DB session logic

router = APIRouter()

@router.get("", response_model=List[schemas.Note])
def list_notes(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(models.Note).filter(models.Note.deleted_at.is_(None)).offset(skip).limit(limit).all()


@router.get("/{note_id}", response_model=schemas.Note)
def read_note(note_id: int, db: Session = Depends(get_db)):
    note = db.query(models.Note).filter(models.Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    # Update last_accessed_at logic here if desired
    return note


@router.post("", response_model=schemas.Note)
def create_note(note: schemas.NoteCreate, db: Session = Depends(get_db)):
    db_note = models.Note(**note.dict())
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note


@router.put("/{note_id}", response_model=schemas.Note)
def update_note(note_id: int, note: schemas.NoteUpdate, db: Session = Depends(get_db)):
    # 1. Fetch the existing record
    db_note = db.query(models.Note).filter(models.Note.id == note_id).first()
    
    # 2. Raise an error if the note doesn't exist
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")

    # 3. Apply updates dynamically
    update_data = note.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_note, key, value)

    # 4. Commit and refresh
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    
    return db_note


@router.delete("/{note_id}")
def soft_delete_note(note_id: int, db: Session = Depends(get_db)):
    db_note = db.query(models.Note).filter(models.Note.id == note_id).first()
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    db_note.deleted_at = datetime.utcnow() # "Delete" it
    db.commit()
    return {"message": "Note moved to trash"}

@router.delete("/purge/{note_id}")
def hard_delete_note(note_id: int, db: Session = Depends(get_db)):
    db_note = db.query(models.Note).filter(models.Note.id == note_id).first()
    
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    if db_note.deleted_at is None:
        raise HTTPException(
            status_code=400, 
            detail="Cannot purge an active note. Soft-delete it first."
        )
    
    db.delete(db_note)
    db.commit()
    return {"message": f"Note {note_id} permanently deleted from trash."}
    