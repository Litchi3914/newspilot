# Stack Preflight Report

- created_at: 2026-04-29T18:13:04
- ready: True

## LLM
- provider: openai
- model: Qwen/Qwen3-8B
- base_url: https://api.siliconflow.cn/v1
- api_key_env: OPENAI_API_KEY
- api_key_present: True
- endpoint_ok: True
- endpoint_message: sdk_chat_ok: ok

## Embedding
- provider: none
- model: bge-m3
- base_url: (empty)
- endpoint_ok: True
- endpoint_message: skipped (embedding sdk probe not enabled in preflight)

## Vectorstore
- backend: faiss
- ready: True
- message: ok

## Python Deps
- openai: installed=True (ok)
- pymilvus: installed=True (ok)
- chromadb: installed=True (ok)
- faiss: installed=True (ok)
