from __future__ import annotations
from datetime import datetime
from uuid import uuid4
from starlette.middleware.base import BaseHTTPMiddleware

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        rid = request.headers.get('X-Request-ID') or f"review_{datetime.now().strftime('%Y%m%d')}_{uuid4().hex[:8]}"
        request.state.request_id = rid
        response = await call_next(request)
        response.headers['X-Request-ID'] = rid
        return response
