from fastapi import FastAPI, Request, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from starlette.middleware.base import BaseHTTPMiddleware


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):

        # 3. Process request
        response = await call_next(request)
        
        response.headers["X-Content-Type-Options"]
        response.headers["X-Frame-Options"]
        response.headers["Content-Security-Policy"]
        


        return response