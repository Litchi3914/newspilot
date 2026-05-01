# API Contract (Draft v0.2)

## 1. POST /api/review

### Request
```json
{
  "title": "新闻稿标题",
  "draft_text": "新闻稿初稿正文",
  "article_type": "auto",
  "options": {
    "retriever": "bm25",
    "enable_retrieval": true,
    "enable_llm": true,
    "enable_diff": true,
    "top_k": 5
  }
}
```

### Response
```json
{
  "request_id": "review_20260429_0001",
  "status": "success",
  "original_title": "原始标题",
  "original_text": "原始正文",
  "detected_type": "会议新闻",
  "rule_check_result": {},
  "retrieval_results": [],
  "llm_review_result": {
    "review_summary": {
      "overall_score": 82,
      "main_problems": ["导语信息不完整"],
      "overall_suggestion": "建议补齐时间地点"
    },
    "issues": [],
    "revised_title": "修订后标题",
    "revised_text": "修订后正文",
    "fact_risks": []
  },
  "revised_title": "修订后标题",
  "revised_text": "修订后正文",
  "diff_ops": [],
  "errors": [],
  "metadata": {
    "provider": "mock",
    "model": "mock",
    "created_at": "2026-04-29T16:00:00",
    "retriever": "bm25",
    "enable_llm": true,
    "enable_diff": true
  }
}
```

### Error Response
```json
{
  "request_id": "review_20260429_0002",
  "status": "partial_success",
  "errors": [
    {
      "stage": "review_article",
      "error_type": "missing_api_key",
      "error_message": "OPENAI_API_KEY is missing."
    }
  ]
}
```

---

## 2. POST /api/retrieve

### Request
```json
{
  "query": "待审新闻稿正文",
  "article_type": "会议新闻",
  "top_k": 5,
  "retriever": "bm25"
}
```

### Response
```json
{
  "results": [
    {
      "title": "参考稿件标题",
      "url": "https://news.hzau.edu.cn/xxx",
      "chunk_text": "相似片段",
      "score": 12.8,
      "article_type": "会议新闻",
      "reason": "结构和主题相似"
    }
  ]
}
```

---

## 3. POST /api/quality-check

### Request
```json
{
  "title": "标题",
  "draft_text": "正文",
  "article_type": "auto"
}
```

### Response
```json
{
  "detected_type": "会议新闻",
  "review_summary": {
    "overall_score": 86,
    "main_problems": ["导语过短"],
    "overall_suggestion": "补充导语核心信息"
  },
  "issues": {
    "element_check": [],
    "language_issues": [],
    "structure_issues": [],
    "fact_risks": []
  }
}
```

---

## 4. Status & Error Codes

- `success`: 全部流程成功
- `partial_success`: 主流程成功但子步骤（通常 LLM）失败并回退
- `failed`: 输入无效或关键步骤失败

建议错误码：
- `invalid_input`
- `missing_api_key`
- `real_call_disabled`
- `llm_timeout`
- `llm_rate_limited`
- `schema_validation_error`
- `internal_error`

---

## 5. Frontend Rendering Notes

前端可直接使用：
1. `revised_text` 渲染清洁稿
2. `diff_ops` 渲染审阅模式
3. `llm_review_result.issues` 渲染侧边问题列表
4. `retrieval_results` 渲染参考范文卡片
