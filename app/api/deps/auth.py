from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
import os
from dotenv import load_dotenv

API_KEY_NAME = "access_token"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# This reads from the OS environment variables
load_dotenv()
EXPECTED_API_KEY = os.getenv("API_ACCESS_TOKEN", "default-secret-change-me")

print(">>>>>>>>>>>>>>>>>", EXPECTED_API_KEY)

def validate_api_key(api_key: str = Security(api_key_header)):
    # In a real app, this might check a DB or Secret Manager
    if api_key != EXPECTED_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Unauthorized: Invalid API Key"
        )
    return api_key