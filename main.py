import uuid
from fastapi import FastAPI, Request, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from middleware.CorrelationMiddleware import CorrelationIdMiddleware 
from middleware.PerformanceMonitorMiddleware import PerformanceMonitorMiddleware

app = FastAPI(title="Basic-CRUD-APP")
          
app.add_middleware(CorrelationIdMiddleware)        
app.add_middleware(PerformanceMonitorMiddleware)

# 2. Security Layer (Simulation of a SASE Policy)
API_KEY_NAME = "access_token"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

def validate_api_key(api_key: str = Security(api_key_header)):
    # In a real Check Point product, this would check a database/LDAP
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

class Note(BaseModel):
    id: str | None = None
    content: str

notes_db = []

@app.post("/notes", status_code=status.HTTP_201_CREATED)
async def create_note(note: Note):
    note.id = str(uuid.uuid4())
    notes_db.append(note.dict())
    return note

@app.get("/notes")
async def get_notes(authorized: bool = Security(validate_api_key)):
    return {"notes": notes_db}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)