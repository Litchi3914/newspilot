# Frontend Integration Guide

## 调用方式
- Endpoint: `/api/v1/review`
- Method: `POST`
- Header: `Content-Type: application/json`

## fetch 示例
```ts
const res = await fetch('/api/v1/review', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    title,
    content,
    source: 'web',
    review_mode: 'standard',
    options: { enable_retrieval: true, enable_llm: true, enable_diff: true }
  })
});
const data = await res.json();
```

## 前端展示关键字段
- 左侧原稿：`data.original.title/content`
- 右侧清洁稿：`data.revised.title/content`
- 审阅模式：`data.diff`
- 问题列表：`data.issues`
- 请求追踪：`request_id`
- 错误提示：`error.message`

## 容错建议
- `data` 可能为 null，渲染前判空
- `diff/issues` 为空数组时显示“暂无”
- 出错时展示 `request_id` 便于排查

## 本地启动（灰度前最小页面）
后端：
```bash
uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000
```

前端：
```bash
cd frontend
npm install
npm run dev
```

浏览器访问：
- http://localhost:5173

说明：
- Vite 已代理 `/api` 到 `http://localhost:8000`。
- 页面请求接口：`POST /api/v1/review`。
