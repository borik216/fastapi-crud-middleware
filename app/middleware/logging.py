import time
import json
import logging
import uuid
import sys
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

# Setup a basic logger to output to stdout (the terminal)
logger = logging.getLogger("vault_access")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)

class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        start_time = time.time()
        
        # Process the request
        response = await call_next(request)
        
        # Calculate how long it took
        process_time = (time.time() - start_time) * 1000  # in milliseconds
        
        # Create a structured log entry
        log_dict = {
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "latency_ms": round(process_time, 2),
            "client_ip": request.client.host if request.client else "unknown"
        }
        
        # Output as a single line of JSON
        # 2. Add it back to the response header so the user can report it
        response.headers["X-Correlation-ID"] = correlation_id
        logger.info(json.dumps(log_dict))
        
        return response