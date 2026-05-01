# SiliconFlow Qwen-3-8B 部署说明

## 1) 安装依赖

```bash
pip install openai python-dotenv
```

## 2) 配置环境变量（项目根目录 `.env`）

```env
LLM_PROVIDER=openai
LLM_ENABLE_REAL_CALL=true
OPENAI_MODEL=Qwen/Qwen3-8B
OPENAI_BASE_URL=https://api.siliconflow.cn/v1
OPENAI_API_KEY=你的_SILICONFLOW_API_KEY
LLM_API_KEY_ENV=OPENAI_API_KEY
LLM_TIMEOUT_SECONDS=60
LLM_MAX_RETRIES=2
LLM_TEMPERATURE=0.2
```

## 3) 预检查

```bash
python scripts/11_stack_preflight.py
```

检查输出文件：

- `data/logs/stack_preflight_report.md`
- `data/logs/stack_preflight_report.json`

目标：`LLM endpoint_ok=true`。

## 4) 单条审稿验证

```bash
python scripts/run_review_demo.py --input examples/sample_draft.txt --retriever bm25 --llm-provider openai --enable-llm --enable-diff --output data/demo_outputs/review_result_full.json
```

## 5) 启动 API 服务验证

```bash
python -m uvicorn src.api.app:app --host 0.0.0.0 --port 8000
```

调用：

- `POST /api/v1/review`

## 6) 常见问题

- 401/403：API Key 错误或未生效。
- 404：`OPENAI_BASE_URL` 不正确，需为 `https://api.siliconflow.cn/v1`。
- 超时：调高 `LLM_TIMEOUT_SECONDS`（如 90）。
- 字段不全：流程会自动 fallback，不会导致主流程崩溃。
