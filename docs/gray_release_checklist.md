# Gray Release Checklist

## 后端
- [ ] /api/v1/review 可稳定调用
- [ ] 统一错误结构可用
- [ ] request_id 贯通响应与日志
- [ ] 超时保护可用（REVIEW_TIMEOUT）
- [ ] 并发限制可用（RATE_LIMITED）
- [ ] mock 模式稳定运行

## 前端联调
- [ ] 可提交标题与正文
- [ ] 可展示修订稿
- [ ] 可展示 diff
- [ ] 可展示问题列表
- [ ] 可展示错误与 request_id

## 质量门禁
- [ ] 有评估集结构（30-50样本）
- [ ] 有评估脚本和报告
- [ ] 成功率 >= 95%
- [ ] 错误率 <= 5%
- [ ] P95 <= 45s
