from __future__ import annotations
import asyncio
import os
from fastapi import APIRouter, Request
from src.api.schemas.review import ReviewRequest, ReviewResponse
from src.api.schemas.errors import APIError, ErrorCode
from src.api.services.review_service import ReviewService

router = APIRouter(tags=['review'])
_service = ReviewService()
_MAX_CONCURRENT = int(os.getenv('MAX_CONCURRENT_REVIEWS', '3'))
_TIMEOUT = int(os.getenv('REVIEW_TIMEOUT_SECONDS', '240'))
_SEM = asyncio.Semaphore(_MAX_CONCURRENT)


def _error_response(rid: str, code: ErrorCode, msg: str, stage: str, recoverable: bool = True) -> ReviewResponse:
    err = APIError(code=code, message=msg, stage=stage, recoverable=recoverable)
    return ReviewResponse(
        request_id=rid,
        status='error',
        original_text='',
        data=None,
        error=err,
        errors=[err],
    )


@router.post('/review', response_model=ReviewResponse)
async def review_route(payload: ReviewRequest, request: Request):
    rid = payload.request_id or getattr(request.state, 'request_id', '')

    if not payload.draft_text or not payload.draft_text.strip():
        return _error_response(rid, ErrorCode.INVALID_INPUT, '请输入有效的新闻稿标题和正文', 'input', True)

    if _SEM.locked() and _SEM._value == 0:
        return _error_response(rid, ErrorCode.RATE_LIMITED, '当前审稿请求较多，请稍后重试', 'rate_limit', True)

    async with _SEM:
        try:
            return await asyncio.wait_for(asyncio.to_thread(_service.review, payload, rid), timeout=_TIMEOUT)
        except asyncio.TimeoutError:
            return _error_response(rid, ErrorCode.REVIEW_TIMEOUT, '审稿请求超时，请稍后重试', 'timeout', True)
        except Exception:
            return _error_response(rid, ErrorCode.INTERNAL_ERROR, '系统异常，请稍后重试', 'api', False)



