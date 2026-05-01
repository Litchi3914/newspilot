import type { ReviewIssue } from "../types/review";

type Props = {
  issues: ReviewIssue[];
};

export default function IssueList({ issues }: Props) {
  return (
    <div className="card">
      <h3>问题列表</h3>
      {issues.length === 0 ? <div className="muted">暂无问题</div> : null}
      {issues.map((x, i) => (
        <div key={i} className="issue-item">
          <div><b>问题类型：</b>{x.issue_type ?? x.category ?? "-"}</div>
          <div><b>严重程度：</b>{x.severity ?? "-"}</div>
          <div><b>问题说明：</b>{x.message ?? x.problem ?? "-"}</div>
          <div><b>修改建议：</b>{x.suggestion ?? "-"}</div>
          <div><b>依据：</b>{x.evidence ?? "-"}</div>
        </div>
      ))}
    </div>
  );
}
