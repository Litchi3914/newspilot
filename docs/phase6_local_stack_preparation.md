# Phase 6/7 部署前准备（Ollama / vLLM / LM Studio + Qwen3-14B + bge-m3 + Milvus/Chroma/FAISS）

## 1. 目标

在不重构现有工程的前提下，先把“可切换部署底座”准备好：

- LLM 走 OpenAI-compatible 接口；
- 默认模型可切到 `Qwen/Qwen3-14B-Instruct`；
- Embedding 预留 `bge-m3` 接口配置；
- 向量库可切换 `milvus/chroma/faiss`；
- 先用 preflight 脚本验证环境是否可跑。

## 2. 已补齐内容

- 扩展 `.env.example`：新增 LLM/Embedding/VectorStore 关键变量；
- 扩展 `configs/llm.yaml`：支持 `base_url` 与 `api_key_env`；
- 升级 `src/llm/factory.py` 与 `src/llm/openai_client.py`：支持 OpenAI-compatible endpoint；
- 新增 `scripts/11_stack_preflight.py`：一键检查端点与依赖。

## 3. 推荐配置（示例）

### 3.1 Ollama + Qwen3-14B

```env
LLM_PROVIDER=openai
LLM_ENABLE_REAL_CALL=true
OPENAI_MODEL=Qwen/Qwen3-14B-Instruct
OPENAI_BASE_URL=http://127.0.0.1:11434/v1
OPENAI_API_KEY=ollama
```

### 3.2 vLLM + Qwen3-14B

```env
LLM_PROVIDER=openai
LLM_ENABLE_REAL_CALL=true
OPENAI_MODEL=Qwen/Qwen3-14B-Instruct
OPENAI_BASE_URL=http://127.0.0.1:8000/v1
OPENAI_API_KEY=local-dev-key
```

### 3.3 LM Studio + Qwen3-14B

```env
LLM_PROVIDER=openai
LLM_ENABLE_REAL_CALL=true
OPENAI_MODEL=Qwen/Qwen3-14B-Instruct
OPENAI_BASE_URL=http://127.0.0.1:1234/v1
OPENAI_API_KEY=lm-studio
```

### 3.4 Embedding（bge-m3）

如果你用独立 embedding 服务（OpenAI-compatible）：

```env
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=bge-m3
EMBEDDING_BASE_URL=http://127.0.0.1:8001/v1
EMBEDDING_API_KEY=local-dev-key
```

## 4. 向量库切换建议

```env
VECTORSTORE_BACKEND=faiss   # 或 milvus/chroma
```

- `faiss`：单机最轻量，适合先跑通；
- `chroma`：本地持久化方便调试；
- `milvus`：后续扩展性更强，适合服务化。

## 5. preflight 检查

运行：

```bash
python scripts/11_stack_preflight.py
```

输出：

- `data/logs/stack_preflight_report.json`
- `data/logs/stack_preflight_report.md`

重点看：

- `LLM endpoint_ok` 是否为 `true`；
- `vectorstore.ready` 是否为 `true`；
- `hard_failures` 是否为空。

## 6. 下一步（建议顺序）

1. 先用 `faiss` 跑通 20 篇小样本真实 LLM。
2. 再切 `chroma` 或 `milvus` 做稳定性验证。
3. 确认审稿输出字段与 API 契约保持一致后，再进入 Web 灰测。
