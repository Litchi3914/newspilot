import type { ReviewDiff } from "../types/review";

type Props = {
  diff: ReviewDiff[];
};

export default function DiffPanel({ diff }: Props) {
  return (
    <div>
      <h3>Diff 对比</h3>
      {diff.length === 0 ? <div className="muted">暂无 diff</div> : null}
      {diff.map((d, i) => (
        <div key={i} className="diff-item">
          <div><b>类型：</b>{d.type}</div>
          <div><b>原文：</b>{d.source_text ?? d.original ?? ""}</div>
          <div><b>修改后：</b>{d.target_text ?? d.revised ?? ""}</div>
          <div><b>原因：</b>{d.reason ?? ""}</div>
        </div>
      ))}
    </div>
  );
}
