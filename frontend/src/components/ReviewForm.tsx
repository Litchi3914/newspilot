import { useState } from "react";

type Props = {
  onSubmit: (args: { title: string; content: string }) => Promise<void>;
  loading: boolean;
};

export default function ReviewForm({ onSubmit, loading }: Props) {
  const [title, setTitle] = useState("学院召开人工智能专题交流会");
  const [content, setContent] = useState(
    "4月8日上午，智育辅导员工作室 AI 辅导员建设专题交流会在水产楼 B205 会议室召开。学工部、学院辅导员和学生代表参加会议。会上，相关负责人介绍建设进展，并围绕后续任务进行交流。"
  );

  const count = content.length;
  const canSubmit = title.trim().length >= 2 && content.trim().length >= 20;

  return (
    <div className="card">
      <h2>稿件输入区</h2>
      <label>标题</label>
      <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="请输入标题" />
      <label>正文</label>
      <textarea value={content} onChange={(e) => setContent(e.target.value)} rows={16} placeholder="请输入正文" />
      <div className="hint">字数：{count}</div>
      <div className="actions">
        <button disabled={loading || !canSubmit} onClick={() => onSubmit({ title, content })}>
          {loading ? "审稿中..." : "开始审稿"}
        </button>
        <button disabled={loading} className="ghost" onClick={() => { setTitle(""); setContent(""); }}>
          清空
        </button>
      </div>
      {!canSubmit && <div className="error">标题至少 2 字，正文至少 20 字。</div>}
    </div>
  );
}
