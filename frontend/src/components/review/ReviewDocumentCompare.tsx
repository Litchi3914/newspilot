import { useMemo, useState } from "react";
import ReviewedDocument from "./ReviewedDocument";
import ReviewModeToggle, { type ReviewDisplayMode } from "./ReviewModeToggle";
import { buildSemanticReviewDiff, getSemanticDiffStats } from "../../utils/reviewDiff";
import "./reviewStyles.css";

type Props = {
  originalTitle?: string;
  originalText: string;
  revisedText: string;
  loading?: boolean;
  hasReviewed?: boolean;
  error?: string | null;
  editableOriginal?: boolean;
  onOriginalTitleChange?: (value: string) => void;
  onOriginalTextChange?: (value: string) => void;
};

export default function ReviewDocumentCompare({
  originalTitle = "",
  originalText,
  revisedText,
  loading = false,
  hasReviewed = false,
  error = null,
  editableOriginal = false,
  onOriginalTitleChange,
  onOriginalTextChange
}: Props) {
  const [mode, setMode] = useState<ReviewDisplayMode>("review");
  const diffOps = useMemo(() => buildSemanticReviewDiff(originalText, revisedText), [originalText, revisedText]);
  const stats = useMemo(() => getSemanticDiffStats(diffOps), [diffOps]);
  const hasResult = hasReviewed && Boolean(revisedText.trim()) && !error;
  const statItems = [
    { label: "新增", count: stats.addCount },
    { label: "删除", count: stats.deleteCount },
    { label: "替换", count: stats.replaceCount },
    { label: "润色", count: stats.rewriteCount },
    { label: "语序调整", count: stats.reorderCount },
    { label: "标点", count: stats.punctuationCount },
    { label: "格式", count: stats.formatCount }
  ].filter((item) => item.count > 0);
  const legendItems = [
    { className: "diff-add", label: "绿色：新增", show: stats.addCount > 0 },
    { className: "diff-delete", label: "红色：删除", show: stats.deleteCount > 0 },
    { className: "diff-replace-revised", label: "绿/红：替换", show: stats.replaceCount > 0 },
    { className: "diff-rewrite", label: "蓝色：表达润色", show: stats.rewriteCount > 0 },
    { className: "diff-reorder", label: "紫色：语序调整", show: stats.reorderCount > 0 },
    { className: "diff-punctuation", label: "黄色：标点调整", show: stats.punctuationCount > 0 },
    { className: "diff-format", label: "灰色：格式调整", show: stats.formatCount > 0 }
  ].filter((item) => !hasResult || item.show);

  return (
    <div className="review-doc-wrap">
      <div className="review-compare-container">
        <section className="review-doc-panel">
          <div className="review-doc-header">原稿</div>
          <div className="review-doc-page">
            {editableOriginal ? (
              <div className="doc-editor">
                <input
                  className="doc-title-input"
                  value={originalTitle}
                  onChange={(e) => onOriginalTitleChange?.(e.target.value)}
                  placeholder="请输入标题"
                />
                <textarea
                  className="doc-textarea"
                  value={originalText}
                  onChange={(e) => onOriginalTextChange?.(e.target.value)}
                  placeholder="请输入新闻稿正文"
                />
              </div>
            ) : (
              originalText || "-"
            )}
          </div>
        </section>

        <section className="review-doc-panel">
          <div className="review-doc-header review-doc-header-with-toolbar">
            <div>
              <div>AI 修订稿 · {mode === "review" ? "审阅模式" : "最终稿模式"}</div>
              {hasResult ? (
                <div className="review-doc-subtitle">
                  {statItems.length > 0
                    ? statItems.map((item) => `${item.label} ${item.count} 处`).join(" / ")
                    : "未发现明显修改"}
                </div>
              ) : null}
            </div>
            <ReviewModeToggle mode={mode} onChange={setMode} />
          </div>
          <div className="review-legend" aria-label="修改类型图例">
            {legendItems.map((item) => (
              <div key={item.label} className="review-legend-item">
                <span className={`review-legend-mark ${item.className}`} />
                <span>{item.label}</span>
              </div>
            ))}
          </div>
          <div className="review-doc-page">
            <ReviewedDocument
              mode={mode}
              revisedText={revisedText}
              diffOps={diffOps}
              loading={loading}
              hasReviewed={hasReviewed}
              hasError={Boolean(error)}
            />
          </div>
        </section>
      </div>
    </div>
  );
}
