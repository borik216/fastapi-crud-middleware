from fastapi import FastAPI, Request, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from starlette.middleware.base import BaseHTTPMiddleware
import uuid


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 1. Get or create correlation ID
        corr_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
        
        # 2. Store it on the request (so endpoints / other middleware can use it)
        request.state.correlation_id = corr_id

        # 3. Process request
        response = await call_next(request)
        
        # 4. Expose it on the response
        response.headers["X-Correlation-ID"] = corr_id

        return response