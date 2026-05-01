# API Review v1

## POST /api/v1/review
- Content-Type: application/json

### 请求字段
| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| request_id | string | 否 | 前端可传，不传后端生成 |
| title | string | 是 | 标题 |
| content | string | 是 | 正文 |
| source | string | 否 | 默认 web |
| review_mode | string | 否 | 默认 standard |
| options.enable_retrieval | bool | 否 | 默认 true |
| options.enable_llm | bool | 否 | 默认 true |
| options.enable_diff | bool | 否 | 默认 true |

### 成功响应（示例）
```json
{
  "request_id": "review_20260429_xxx",
  "status": "success",
  "data": {
    "original": {"title": "原始标题", "content": "原始正文"},
    "revised": {"title": "修订标题", "content": "修订正文"},
    "diff": [],
    "issues": [],
    "summary": {"overall_comment": "整体可用", "risk_level": "low", "suggestion_count": 2}
  },
  "error": null,
  "meta": {"api_version": "v1", "model": "mock", "retriever": "bm25", "elapsed_ms": 1200}
}
```

### 失败响应（示例）
```json
{
  "request_id": "review_20260429_xxx",
  "status": "error",
  "data": null,
  "error": {"code": "REVIEW_TIMEOUT", "message": "审稿请求超时，请稍后重试", "detail": "review pipeline exceeded timeout"},
  "meta": {"api_version": "v1", "elapsed_ms": 30000}
}
```

### curl 示例
```bash
curl -X POST "http://localhost:8000/api/v1/review" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "学院召开人工智能专题交流会",
    "content": "4月28日上午，智芯辅导员工作室 AI 辅导员建设专题交流会在水产楼 B205 会议室召开...",
    "source": "web",
    "review_mode": "standard",
    "options": {"enable_retrieval": true, "enable_llm": true, "enable_diff": true}
  }'
```

### 错误码
- INVALID_INPUT
- REVIEW_TIMEOUT
- RATE_LIMITED
- LLM_PROVIDER_ERROR
- RETRIEVAL_ERROR
- DIFF_ERROR
- INTERNAL_ERROR
