import type { ReviewResponse } from "../types/review";
import DiffPanel from "./DiffPanel";
import IssueList from "./IssueList";
import ReviewDocumentCompare from "./review/ReviewDocumentCompare";

type Props = {
  result: ReviewResponse | null;
  loading: boolean;
};

function normalize(result: ReviewResponse) {
  const data = result.data;
  const originalTitle = data?.original?.title ?? result.original_title ?? "";
  const originalContent = data?.original?.content ?? result.original_text ?? "";
  const revisedTitle = data?.revised?.title ?? result.revised_title ?? "";
  const revisedContent =
    data?.revised_text ??
    data?.revised?.content ??
    result.revised_text ??
    result.llm_review?.revised_text ??
    "";
  const diff = data?.diff ?? result.diff_ops ?? [];
  const issues = data?.issues ?? result.llm_review_result?.issues ?? [];
  const overall =
    data?.summary?.overall_comment ??
    result.llm_review_result?.review_summary?.overall_suggestion ??
    "";
  const requestId = result.request_id ?? "";
  return {
    originalTitle,
    originalContent,
    revisedTitle,
    revisedContent,
    diff,
    issues,
    overall,
    requestId
  };
}

export default function ReviewResult({ result, loading }: Props) {
  if (loading) {
    return (
      <div className="card">
        <h2>审稿结果区</h2>
        <div className="muted">正在分析稿件，请稍候...</div>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="card">
        <h2>审稿结果区</h2>
        <div className="muted">提交稿件后在此展示结果。</div>
      </div>
    );
  }

  const n = normalize(result);

  return (
    <div className="result-stack">
      <div className="card">
        <h2>审稿文档对比</h2>
        <div className="meta">
          request_id: {n.requestId || "-"}
          {n.originalTitle ? ` | 原标题: ${n.originalTitle}` : ""}
          {n.revisedTitle ? ` | 修订标题: ${n.revisedTitle}` : ""}
        </div>
        <ReviewDocumentCompare
          originalText={n.originalContent || ""}
          revisedText={n.revisedContent || ""}
          hasReviewed={Boolean(result)}
          error={result.error?.message ?? null}
        />
      </div>

      <IssueList issues={n.issues} />

      <details className="card">
        <summary>查看原始 Diff（调试）</summary>
        <DiffPanel diff={n.diff} />
      </details>

      <div className="card">
        <h3>整体建议</h3>
        <div>{n.overall || "暂无"}</div>
      </div>
    </div>
  );
}
