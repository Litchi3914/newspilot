# NewsPilot 产品进度实现文档

- 文档日期：2026-04-30
- 面向对象：产品经理 / 项目协同评审
- 当前阶段：从 Demo 闭环进入 Web 灰测准备
- 当前结论：核心审稿链路已跑通，前后端最小闭环已具备；下一步重点应放在“真实模型稳定性、评估集、灰度门禁”。

---

## 1. 一页结论

NewsPilot 当前已经完成从新闻稿输入、规则检查、范文检索、AI 审稿、修订稿生成、差异展示到请求日志记录的主链路搭建，具备给 PM 演示和进入小范围灰测准备的基础。

已确认可用：

1. 数据采集、解析、结构化、分类、切块流程。
2. BM25/TF-IDF/Hybrid 检索接口，其中当前默认 BM25。
3. 新闻要素检查与审稿 Pipeline。
4. OpenAI-compatible LLM 接入预留，可切换 mock/openai。
5. `/api/v1/review` 后端审稿接口。
6. 前端 React/Vite 最小工作台，可提交标题和正文，并展示原稿、AI 修订稿、diff、问题提示、request_id。
7. 请求日志、LLM 调用日志、API 超时和并发保护。

当前不建议对外承诺：

1. 完全自动替代人工审稿。
2. 所有稿件类型都有稳定高质量建议。
3. 大批量并发审稿。
4. 无需人工评估即可判断模型建议质量。

---

## 2. 当前产品能力清单

| 模块 | 实现状态 | 产品可见能力 | 说明 |
|---|---:|---|---|
| 新闻数据采集 | 已完成 Demo | 可采集公开栏目新闻 | 低频、非并发、保留 URL/source_site/crawled_at |
| 正文解析清洗 | 已完成 Demo | 将网页新闻转为正文与段落 | 当前质量报告显示解析成功率 100% |
| 稿件类型识别 | 已完成 Demo | 自动识别会议新闻、活动纪实等 | 规则分类可解释，但长尾类型样本不足 |
| 文本切块 | 已完成 Demo | 为检索和审稿提供 chunk | 已产出 472 个 chunk |
| 相似范文检索 | 已完成 Demo | 返回 Top-K 相似范文 | 当前默认 BM25，向量检索为预留方向 |
| 新闻要素检查 | 已完成 Demo | 检查标题、时间、地点、人物、事件等 | 对会议新闻/活动纪实/科研成果覆盖较好 |
| AI 审稿 Pipeline | 已完成 Demo | 生成问题清单、修改建议、修订稿 | 支持 mock 与 OpenAI-compatible 服务 |
| 文本差异展示 | 已完成 Demo | 展示原稿与 AI 修订稿差异 | 前端已接入 diff 数据兼容层 |
| 后端 API | 已实现 v1 | `POST /api/v1/review` | 支持 request_id、错误结构、超时、限流 |
| 前端工作台 | 已实现最小版 | 输入稿件并查看审稿结果 | React + Vite，已通过生产构建 |
| 日志与追踪 | 已实现基础版 | 记录 API 请求与 LLM 调用 | 可用于灰测排查和耗时统计 |
| 部署预检 | 已完成脚本 | 检查 LLM/Embedding/VectorStore 配置 | `scripts/11_stack_preflight.py` |

---

## 3. 已实现链路

### 3.1 离线数据链路

当前离线链路已经形成可重复执行流程：

1. 栏目采集：`scripts/01_crawl_categories.py`
2. 正文解析：`scripts/02_parse_articles.py`
3. 结构化导出：`scripts/03_export_structured_csv.py`
4. 类型标注：`scripts/04_label_article_type.py`
5. chunk 构建：`scripts/05_build_chunks.py`
6. 检索索引：`scripts/06_build_vector_index.py` / `scripts/build_index.py`
7. 质量检查：`scripts/07_quality_check.py`
8. 检索演示：`scripts/08_retrieval_demo.py`
9. 要素检查演示：`scripts/09_element_check_demo.py`
10. 审稿演示：`scripts/10_review_demo.py`

### 3.2 在线审稿链路

当前在线链路如下：

1. 前端提交标题和正文。
2. 后端接收 `POST /api/v1/review`。
3. 后端生成或透传 `request_id`。
4. ReviewService 调用 ReviewPipeline。
5. Pipeline 执行类型识别、规则检查、BM25 检索、LLM 审稿、diff 生成。
6. 后端返回结构化审稿结果。
7. 前端展示原稿、AI 修订稿、差异片段、问题列表、错误提示和 request_id。
8. 后端写入 API 请求日志与 LLM 调用日志。

---

## 4. 当前数据与质量基线

截至 2026-04-30，沿用上一轮补样后的质量基线：

| 指标 | 当前值 |
|---|---:|
| 文章总数 | 120 |
| chunk 总数 | 472 |
| 解析成功率 | 100% |
| 正文小于 100 字 | 0 |
| 标题缺失 | 0 |
| 正文缺失 | 0 |
| 发布时间缺失 | 0 |
| URL 缺失 | 0 |
| source_site 缺失 | 0 |
| 平均正文字数 | 1593.35 |
| 平均段落数 | 10.77 |
| 平均每篇 chunk 数 | 3.93 |

稿件类型分布：

| 类型 | 数量 | 占比 |
|---|---:|---:|
| 会议新闻 | 63 | 52.50% |
| 活动纪实 | 40 | 33.33% |
| 科研成果 | 7 | 5.83% |
| 人才培养 | 6 | 5.00% |
| 对外交流 | 3 | 2.50% |
| 人物通讯 | 1 | 0.83% |

产品判断：

1. 会议新闻、活动纪实已经具备较好的 Demo 覆盖。
2. 科研成果、人才培养、对外交流、人物通讯仍是长尾类型，建议后续定向补样。
3. 质量基线足够支撑灰测准备，但不足以支撑正式上线判断。

---

## 5. API 与前端进度

### 5.1 后端 API

已实现：

1. `POST /api/v1/review`
2. `ReviewRequest` 参数兼容 `content` 和 `draft_text`
3. `ReviewResponse` 返回审稿结果、规则检查结果、检索结果、LLM 审稿结果、diff、错误信息、metadata
4. `RequestIDMiddleware`
5. 统一异常处理
6. 最大并发限制：默认 3
7. 审稿超时保护：默认 240 秒
8. API 请求日志：`data/logs/api_request_log.csv`
9. LLM 调用日志：`data/logs/llm_call_log.csv`

需要同步优化：

1. `docs/api_review_v1.md` 中的示例响应以 `data` 聚合结构为主；当前后端仍主要返回兼容字段，`data` 字段未完全填充。
2. 错误码文档中有 `LLM_PROVIDER_ERROR`，代码中实际还有 `LLM_CALL_FAILED`、`PIPELINE_FAILED` 等内部错误码，需要统一命名。

### 5.2 前端工作台

已实现：

1. 标题输入。
2. 正文输入。
3. 开始审稿按钮。
4. 清空按钮。
5. loading 状态。
6. request_id 展示。
7. 错误提示。
8. 原稿与 AI 修订稿双栏展示。
9. diff 片段渲染。
10. 问题列表兼容展示。
11. 前端请求超时保护：250 秒。

技术栈：

1. React 18
2. TypeScript
3. Vite

验证状态：

1. `npm.cmd run build` 已通过。
2. 构建产物已生成到 `frontend/dist`。

---

## 6. 当前风险与产品决策点

| 优先级 | 风险/问题 | 影响 | 建议 |
|---|---|---|---|
| P0 | 缺少人工评估集 | 无法量化审稿建议是否真的可用 | 先建立 30-50 条人工标注评估集 |
| P0 | 真实 LLM 调用耗时波动 | 影响灰测体验和接口超时 | 明确灰测模型、超时、降级策略 |
| P0 | API 契约与实现存在轻微偏差 | 前后端后续集成容易反复 | 统一 `ReviewResponse.data` 聚合结构或明确兼容期 |
| P1 | 类型分布偏斜 | 长尾稿件建议质量不足 | 按稿件类型定向补样 |
| P1 | chunk 长度仍需优化 | 影响检索相关性和范文可读性 | 目标调整到 200-800 字区间 |
| P1 | 向量检索尚未真正落地 | 语义召回能力有限 | 先以 BM25 为基线，再接 bge-m3 + FAISS/Chroma |
| P2 | 前端仍是最小工作台 | 还不是完整产品界面 | 补充结果导出、历史记录、审稿配置项 |

---

## 7. 下一阶段建议排期

### Day 1-2：灰测门禁补齐

1. 对齐 API 契约与实际响应结构。
2. 固化错误码、错误展示和 request_id 排查路径。
3. 新建 30-50 条人工评估集。
4. 输出第一版评估指标：成功率、建议可用率、修订有效率、P95 耗时。

### Day 3-4：真实模型与检索优化

1. 选择灰测模型配置，优先 OpenAI-compatible endpoint。
2. 跑通真实 LLM 的 20 条样本稳定性测试。
3. 建立 BM25 基线报告。
4. 试接 bge-m3 + FAISS/Chroma 小样本向量检索。

### Day 5：产品化前端增强

1. 增加审稿模式配置入口。
2. 增加结果导出能力。
3. 增加审稿历史或本地最近记录。
4. 优化移动端和窄屏展示。
5. 补齐灰度发布 checklist。

---

## 8. PM 本周需要确认

1. 灰测对象：内部编辑、学院通讯员，还是研发/产品自测？
2. 首批重点稿件类型：会议新闻、活动纪实是否优先？
3. 审稿输出形式：只给问题清单，还是必须给完整修订稿？
4. 风险等级表达：是否需要“低/中/高”或“可发布/需修改/退回重写”？
5. 灰测成功标准：建议采纳率、人工满意度、审稿耗时分别达到什么线？

---

## 9. 当前交付物索引

文档：

1. `docs/stage_acceptance_for_pm_2026-04-29.md`
2. `docs/api_review_v1.md`
3. `docs/frontend_integration_guide.md`
4. `docs/gray_release_checklist.md`
5. `docs/phase6_local_stack_preparation.md`

核心代码：

1. `src/api/app.py`
2. `src/api/routes/review.py`
3. `src/api/services/review_service.py`
4. `src/reviewer/review_pipeline.py`
5. `frontend/src/App.tsx`
6. `frontend/src/api/review.ts`
7. `frontend/src/components/review/ReviewDocumentCompare.tsx`

数据与日志：

1. `data/clean_jsonl/articles_clean.jsonl`
2. `data/chunks/article_chunks.jsonl`
3. `data/logs/quality_report_refill.csv`
4. `data/logs/api_request_log.csv`
5. `data/logs/llm_call_log.csv`
6. `data/demo_outputs/review_result_full.json`

---

## 10. 验证记录

已验证：

1. 前端生产构建：通过。
   - 命令：`npm.cmd run build`
   - 结果：TypeScript 编译与 Vite 构建成功。

未完成验证：

1. 后端单元测试未执行成功。
   - 命令：`python -m pytest`
   - 原因：当前 Python 环境缺少 `pytest`。
   - 建议：补充测试依赖或将 `pytest` 写入开发依赖后再执行回归。

---

## 11. 阶段结论

当前项目已经从“算法与数据 Demo”推进到“可联调的产品雏形”。下一阶段不建议继续单纯扩数据量，而应优先完成灰测门禁、人工评估集、真实模型稳定性和 API 契约收口。

推荐 PM 将下一阶段目标定义为：

> 小范围灰测准备：以会议新闻/活动纪实为首批场景，验证审稿建议是否可被人工采纳，并用日志和评估集驱动下一轮模型与检索优化。
