export type ReviewStatus = "success" | "partial_success" | "failed" | "error";

export interface ReviewRequest {
  request_id?: string;
  title: string;
  content: string;
  source?: string;
  review_mode?: string;
  options?: {
    retriever?: "bm25" | "tfidf" | "hybrid";
    llm_provider?: "mock" | "openai";
    enable_retrieval?: boolean;
    enable_llm?: boolean;
    enable_diff?: boolean;
  };
}

export interface ReviewIssue {
  issue_type?: string;
  severity?: string;
  message?: string;
  suggestion?: string;
  evidence?: string;
  category?: string;
  problem?: string;
}

export interface ReviewDiff {
  type: string;
  source_text?: string;
  target_text?: string;
  reason?: string;
  original?: string;
  revised?: string;
  category?: string;
}

export interface ReviewResponse {
  request_id: string;
  status: ReviewStatus;
  data: null | {
    original_text?: string;
    revised_text?: string;
    original: { title: string; content: string };
    revised: { title: string; content: string };
    diff: ReviewDiff[];
    issues: ReviewIssue[];
    summary: {
      overall_comment?: string;
      risk_level?: string;
      suggestion_count?: number;
    };
  };
  error: null | {
    code: string;
    message: string;
    detail?: string;
  };
  meta: {
    api_version?: string;
    model?: string;
    retriever?: string;
    elapsed_ms?: number;
  };

  // backward compatibility with current backend flattened fields
  original_title?: string;
  original_text?: string;
  revised_title?: string;
  revised_text?: string;
  diff_ops?: ReviewDiff[];
  llm_review_result?: {
    review_summary?: {
      overall_suggestion?: string;
      overall_score?: number;
      main_problems?: string[];
    };
    issues?: ReviewIssue[];
  };
  llm_review?: {
    revised_text?: string;
  };
  metadata?: {
    retriever?: string;
    model?: string;
  };
}
