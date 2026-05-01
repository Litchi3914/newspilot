import type { ReviewChangeOp } from "../../utils/reviewDiff";

type Props = {
  op: ReviewChangeOp;
};

function getFallbackText(op: ReviewChangeOp): string {
  return op.text || op.revisedText || op.originalText || "";
}

function buildTitle(label: string, op: ReviewChangeOp): string {
  const originalText = op.originalText || "";
  const revisedText = op.revisedText || "";
  const reason = op.reason ? `${op.reason}\n` : "";
  return `${label}\n${reason}原文：${originalText}\n改为：${revisedText}`;
}

export default function DiffToken({ op }: Props) {
  if (op.type === "equal") {
    return <span>{op.text}</span>;
  }

  if (op.type === "add") {
    return <span className="diff-token diff-add">{op.text || op.revisedText}</span>;
  }

  if (op.type === "delete") {
    return <span className="diff-token diff-delete">{op.text || op.originalText}</span>;
  }

  if (op.type === "replace") {
    return (
      <span className="diff-replace" title={buildTitle("内容替换", op)}>
        <span className="diff-token diff-replace-original">{op.originalText}</span>
        <span className="diff-token diff-replace-revised">{op.revisedText}</span>
      </span>
    );
  }

  if (op.type === "rewrite") {
    return (
      <span className="diff-token diff-rewrite" title={buildTitle("表达润色", op)}>
        {op.revisedText}
      </span>
    );
  }

  if (op.type === "reorder" || op.type === "move") {
    return (
      <span className="diff-token diff-reorder" title={buildTitle("语序调整", op)}>
        {op.revisedText}
      </span>
    );
  }

  if (op.type === "punctuation") {
    return (
      <span className="diff-token diff-punctuation" title={buildTitle("标点调整", op)}>
        {op.revisedText}
      </span>
    );
  }

  if (op.type === "format") {
    return (
      <span className="diff-token diff-format" title={buildTitle("格式调整", op)}>
        {op.revisedText || op.text}
      </span>
    );
  }

  return <span>{getFallbackText(op)}</span>;
}
