export type ReviewDisplayMode = "review" | "final";

type Props = {
  mode: ReviewDisplayMode;
  onChange: (mode: ReviewDisplayMode) => void;
};

export default function ReviewModeToggle({ mode, onChange }: Props) {
  return (
    <div className="review-mode-toggle" aria-label="AI 修订稿显示模式">
      <button
        type="button"
        className={mode === "review" ? "active" : ""}
        onClick={() => onChange("review")}
      >
        审阅模式
      </button>
      <button
        type="button"
        className={mode === "final" ? "active" : ""}
        onClick={() => onChange("final")}
      >
        最终稿模式
      </button>
    </div>
  );
}
