import DiffToken from "./DiffToken";
import type { ReviewDisplayMode } from "./ReviewModeToggle";
import type { ReviewChangeOp } from "../../utils/reviewDiff";

type Props = {
  mode: ReviewDisplayMode;
  revisedText: string;
  diffOps: ReviewChangeOp[];
  loading?: boolean;
  hasReviewed?: boolean;
  hasError?: boolean;
};

export default function ReviewedDocument({
  mode,
  revisedText,
  diffOps,
  loading = false,
  hasReviewed = false,
  hasError = false
}: Props) {
  if (loading) {
    return <div className="review-empty review-loading">AI 正在生成修订稿...</div>;
  }

  if (!hasReviewed) {
    return <div className="review-empty">审稿完成后将在此展示 AI 修订稿</div>;
  }

  if (hasError || !revisedText.trim()) {
    return <div className="review-empty">本次审稿未返回修订稿</div>;
  }

  if (mode === "final") {
    return <div className="review-final-text">{revisedText}</div>;
  }

  return (
    <div className="review-diff-text">
      {diffOps.map((item) => (
        <DiffToken key={item.id} op={item} />
      ))}
    </div>
  );
}
