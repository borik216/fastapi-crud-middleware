from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from datetime import datetime
from app.database import SessionLocal
from app.models import Note

class SecretAccessMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Only trigger for successful GET requests to specific notes
        if request.method == "GET" and "/notes/" in request.url.path:
            # Extract the ID from the path (e.g., /notes/1)
            path_parts = request.url.path.split("/")
            try:
                note_id = int(path_parts[-1])
                
                # We open a dedicated DB session for the background update
                db = SessionLocal()
                note = db.query(Note).filter(Note.id == note_id).first()
                if note:
                    note.last_accessed_at = datetime.utcnow()
                    db.commit()
                db.close()
            except (ValueError, IndexError):
                pass # Path wasn't actually an ID
                
        return response