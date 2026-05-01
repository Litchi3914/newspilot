export type ChangeType =
  | "unchanged"
  | "punctuation"
  | "expression"
  | "addition"
  | "deletion"
  | "structure"
  | "fact"
  | "other";

export interface ReviewSegment {
  id: string;
  text: string;
  type: ChangeType;
  reason?: string;
  before?: string;
  after?: string;
  issueId?: string;
}

export interface DiffLike {
  type?: string;
  source_text?: string;
  target_text?: string;
  reason?: string;
  original?: string;
  revised?: string;
  category?: string;
}

export interface IssueLike {
  id?: string;
  issue_type?: string;
  category?: string;
  severity?: string;
  message?: string;
  problem?: string;
  suggestion?: string;
  evidence?: string;
  before?: string;
  after?: string;
}

function mapType(raw?: string): ChangeType {
  const t = (raw || "").toLowerCase();
  if (t.includes("punct")) return "punctuation";
  if (t.includes("express")) return "expression";
  if (t.includes("add") || t.includes("insert")) return "addition";
  if (t.includes("delet") || t.includes("remove")) return "deletion";
  if (t.includes("struct")) return "structure";
  if (t.includes("fact") || t.includes("risk")) return "fact";
  if (!t || t === "equal" || t === "unchanged") return "unchanged";
  return "other";
}

export function getChangeClass(type: ChangeType): string {
  return `review-segment change-${type}`;
}

export function getChangeTypeLabel(type: ChangeType): string {
  switch (type) {
    case "punctuation":
      return "标点修改";
    case "expression":
      return "表达优化";
    case "addition":
      return "新增内容";
    case "deletion":
      return "删除内容";
    case "structure":
      return "结构调整";
    case "fact":
      return "事实/规范风险";
    case "unchanged":
      return "未修改";
    default:
      return "其他";
  }
}

export function getSegmentTooltip(segment: ReviewSegment): string {
  const parts = [
    `类型：${getChangeTypeLabel(segment.type)}`,
    segment.reason ? `原因：${segment.reason}` : "",
    segment.before ? `修改前：${segment.before}` : "",
    segment.after ? `修改后：${segment.after}` : ""
  ].filter(Boolean);
  return parts.join("\n");
}

function splitByNeedle(text: string, needle: string, replacement: ReviewSegment): ReviewSegment[] {
  if (!needle) return [{ id: `seg-${Math.random()}`, text, type: "unchanged" }];
  const idx = text.indexOf(needle);
  if (idx < 0) return [{ id: `seg-${Math.random()}`, text, type: "unchanged" }];

  const out: ReviewSegment[] = [];
  const head = text.slice(0, idx);
  const tail = text.slice(idx + needle.length);
  if (head) out.push({ id: `seg-${Math.random()}`, text: head, type: "unchanged" });
  out.push({ ...replacement, id: replacement.id || `seg-${Math.random()}` });
  if (tail) out.push({ id: `seg-${Math.random()}`, text: tail, type: "unchanged" });
  return out;
}

function mergeSegments(segments: ReviewSegment[]): ReviewSegment[] {
  const merged: ReviewSegment[] = [];
  for (const seg of segments) {
    const prev = merged[merged.length - 1];
    if (prev && prev.type === seg.type && prev.reason === seg.reason && prev.issueId === seg.issueId) {
      prev.text += seg.text;
    } else {
      merged.push({ ...seg });
    }
  }
  return merged;
}

function applyIssueHighlights(baseText: string, issues: IssueLike[] = []): ReviewSegment[] {
  let segments: ReviewSegment[] = [{ id: "base", text: baseText, type: "unchanged" }];

  issues.forEach((issue, i) => {
    const needle = (issue.after || issue.before || issue.problem || issue.message || "").trim();
    if (!needle) return;

    const next: ReviewSegment[] = [];
    let replaced = false;

    for (const seg of segments) {
      if (seg.type !== "unchanged" || replaced) {
        next.push(seg);
        continue;
      }
      const split = splitByNeedle(seg.text, needle, {
        id: issue.id || `issue-${i}`,
        text: needle,
        type: mapType(issue.issue_type || issue.category),
        reason: issue.suggestion || issue.message || issue.problem,
        before: issue.before,
        after: issue.after,
        issueId: issue.id || `issue-${i}`
      });
      if (split.length > 1) replaced = true;
      next.push(...split);
    }

    segments = next;
  });

  return mergeSegments(segments);
}

export function buildSegmentsFromDiff(diff: DiffLike[] = []): ReviewSegment[] {
  const segments: ReviewSegment[] = [];
  diff.forEach((item, i) => {
    const text = (item.target_text || item.revised || item.source_text || item.original || "").toString();
    if (!text) return;
    segments.push({
      id: `diff-${i}`,
      text,
      type: mapType(item.type || item.category),
      reason: item.reason,
      before: item.source_text || item.original,
      after: item.target_text || item.revised
    });
  });
  return mergeSegments(segments);
}

export function buildReviewSegments(originalText: string, revisedText: string, diff: DiffLike[] = [], issues: IssueLike[] = []): ReviewSegment[] {
  const fromDiff = buildSegmentsFromDiff(diff);
  if (fromDiff.length > 0) return fromDiff;
  return applyIssueHighlights(revisedText || originalText || "", issues);
}
