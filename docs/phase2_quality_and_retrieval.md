# Phase2+ 质量与检索

1. 先执行 `07_quality_check.py`，确认字段完整度、chunk 长度与分类分布。
2. 再执行 `08_retrieval_demo.py`，验证待审稿能返回 3-5 条相似范文。
3. 检索结果可直接供 `10_review_demo.py` 复用。

建议验收：
- 解析成功率 >= 95%
- 标题/正文/发布时间缺失接近 0
- 过短和过长 chunk 占比可控
