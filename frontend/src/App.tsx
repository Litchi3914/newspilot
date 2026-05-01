import { useMemo, useState } from "react";
import { reviewArticle } from "./api/review";
import ErrorAlert from "./components/ErrorAlert";
import IssueList from "./components/IssueList";
import ReviewDocumentCompare from "./components/review/ReviewDocumentCompare";
import type { ReviewResponse } from "./types/review";

const DEFAULT_LLM_PROVIDER = import.meta.env.VITE_LLM_PROVIDER === "openai" ? "openai" : "mock";

function normalize(result: ReviewResponse | null, submittedContent: string) {
  if (!result) {
    return {
      originalText: submittedContent,
      revisedText: "",
      issues: [],
      requestId: ""
    };
  }

  const data = result.data;
  return {
    originalText: submittedContent || data?.original_text || data?.original?.content || result.original_text || "",
    revisedText:
      data?.revised_text ??
      data?.revised?.content ??
      result.revised_text ??
      result.llm_review?.revised_text ??
      "",
    issues: data?.issues ?? result.llm_review_result?.issues ?? [],
    requestId: result.request_id ?? ""
  };
}

export default function App() {
  const [title, setTitle] = useState("学院召开人工智能专题交流会");
  const [content, setContent] = useState(
    "4月8日上午，智育辅导员工作室 AI 辅导员建设专题交流会在水产楼 B205 会议室召开。学工部、学院辅导员和学生代表参加会议。会上，相关负责人介绍建设进展，并围绕后续任务进行交流。"
  );
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ReviewResponse | null>(null);
  const [error, setError] = useState("");

  const normalized = useMemo(() => normalize(result, content), [result, content]);

  const canSubmit = title.trim().length >= 2 && content.trim().length >= 20;

  async function handleReview() {
    if (!canSubmit || loading) return;
    setLoading(true);
    setError("");
    setResult(null);

    const res = await reviewArticle({
      title,
      content,
      source: "web",
      review_mode: "standard",
      options: {
        retriever: "bm25",
        llm_provider: DEFAULT_LLM_PROVIDER,
        enable_retrieval: true,
        enable_llm: true,
        enable_diff: true
      }
    });

    setResult(res);
    if (res.status === "error" || res.status === "failed") {
      setError(res.error?.message || "审稿失败");
    }
    setLoading(false);
  }

  return (
    <div className="workbench">
      <div className="topbar">
        <button onClick={handleReview} disabled={!canSubmit || loading}>
          {loading ? "审稿中..." : "开始审稿"}
        </button>
        <button
          className="ghost"
          disabled={loading}
          onClick={() => {
            setTitle("");
            setContent("");
            setResult(null);
            setError("");
            setLoading(false);
          }}
        >
          清空
        </button>
        <span className="meta">{normalized.requestId ? `request_id: ${normalized.requestId}` : ""}</span>
      </div>

      <ErrorAlert message={error} requestId={normalized.requestId} />

      <ReviewDocumentCompare
        originalTitle={title}
        originalText={normalized.originalText}
        revisedText={normalized.revisedText}
        loading={loading}
        hasReviewed={Boolean(result)}
        error={error}
        editableOriginal
        onOriginalTitleChange={setTitle}
        onOriginalTextChange={setContent}
      />

      {result ? <IssueList issues={normalized.issues} /> : null}
    </div>
  );
}
