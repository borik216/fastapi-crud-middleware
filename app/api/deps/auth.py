from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader

API_KEY_NAME = "access_token"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

def validate_api_key(api_key: str = Security(api_key_header)):
    # In a real app, this might check a DB or Secret Manager
    if api_key != "cp-secure-key-2026":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Could not validate credentials"
        )
    return api_key