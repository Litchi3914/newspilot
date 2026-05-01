from __future__ import annotations
from fastapi import Request
from fastapi.responses import JSONResponse
from src.api.schemas.errors import ErrorCode

async def unhandled_exception_handler(request: Request, exc: Exception):
    rid = getattr(request.state, 'request_id', '')
    return JSONResponse(
        status_code=500,
        content={
            'request_id': rid,
            'status': 'failed',
            'errors': [
                {
                    'code': ErrorCode.UNKNOWN_ERROR.value,
                    'message': 'Internal server error.',
                    'stage': 'api',
                    'recoverable': False,
                }
            ],
        },
    )
