from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time

class PerformanceMonitorMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()
        
        # Process the request
        response = await call_next(request)
        # Calculate Latency (The time taken)
        process_time = time.perf_counter() - start_time
        
        # Attach the metric to the response header (standard R&D practice)
        response.headers["X-Process-Time"] = f"{process_time:.4f}s"
        
        # Log to console for monitoring (Real roles would use Datadog/Grafana here)
        print(f"KPI - {request.method} {request.url.path} | Latency: {process_time:.4f}s")
        return response