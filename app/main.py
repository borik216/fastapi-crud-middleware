from fastapi import FastAPI, HTTPException, Security, status, Depends
from fastapi.security import APIKeyHeader
from app.middleware.correlation import CorrelationIdMiddleware 
from app.middleware.latency_logging import PerformanceMonitorMiddleware
from . import models, database
from fastapi.middleware.cors import CORSMiddleware
from app.middleware.logging import StructuredLoggingMiddleware
from datetime import datetime
from app.api import notes
from app.api.deps.auth import validate_api_key

models.Base.metadata.create_all(bind=database.engine)
app = FastAPI(title="Basic-CRUD-APP")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://secure-notes.example.com"], # Only allow your frontend
    allow_methods=["GET", "POST"],
    allow_headers=["X-API-KEY", "Content-Type"],
)
app.add_middleware(CorrelationIdMiddleware)        
app.add_middleware(PerformanceMonitorMiddleware)
app.add_middleware(StructuredLoggingMiddleware)


app.include_router(notes.router, prefix="/api/v1/notes", tags=["notes"], dependencies=[Security(validate_api_key)])

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
    
    
    
    
    
    
    
    
    
# app.add_middleware(SecretAccessMiddleware)

API_KEY_NAME = "access_token"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

def validate_api_key(api_key: str = Security(api_key_header)):
    if api_key != "cp-secure-key-2026":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Unauthorized Access"
        )
    return True