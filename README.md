# NewsPilot Core Demo

## 安装
```bash
pip install -r requirements.txt
```

## 运行
```bash
python scripts/run_quality_check.py
python scripts/run_chunk.py
python scripts/build_index.py --retriever bm25
python scripts/run_retrieval_demo.py --query "信息学院召开人工智能专题交流会" --top_k 5
python scripts/run_review_demo.py --input examples/sample_draft.txt --retriever bm25
python scripts/run_diff_demo.py --original examples/sample_draft.txt --revised outputs/revised_text.txt
python scripts/run_eval.py
```

## 说明
- 当前支持 TF-IDF/BM25/Hybrid（向量为占位接口）
- 当前 LLM 为 mock 客户端，接口已预留
- 输出以 JSON 为主，Markdown 供人工阅读
