import { diffChars } from "diff";

export type ReviewChangeType =
  | "equal"
  | "add"
  | "delete"
  | "replace"
  | "rewrite"
  | "reorder"
  | "move"
  | "punctuation"
  | "format";

export interface ReviewChangeOp {
  id: string;
  type: ReviewChangeType;
  text?: string;
  originalText?: string;
  revisedText?: string;
  reason?: string;
  confidence?: number;
}

export type ReviewDiffOp = ReviewChangeOp;

const PUNCTUATION_REGEX = /[，。！？；：“”‘’、,.!?;:"'\s]/g;
const FORMAT_REGEX = /\s+/g;
const REWRITE_SIMILARITY_THRESHOLD = 0.55;
const REWRITE_LENGTH_RATIO_THRESHOLD = 0.45;
const REORDER_SIMILARITY_THRESHOLD = 0.6;
const REORDER_NGRAM_THRESHOLD = 0.35;
const LOCAL_EQUAL_CONTEXT_LIMIT = 8;

const NEWS_ENTITY_KEYWORDS = [
  "会议",
  "活动",
  "论坛",
  "讲座",
  "培训",
  "交流会",
  "座谈会",
  "推进会",
  "研讨会",
  "工作室",
  "信息学院",
  "本科生院",
  "党委",
  "水产楼"
];

function buildBaseDiff(originalText: string, revisedText: string): ReviewChangeOp[] {
  if (!originalText && !revisedText) return [];

  return diffChars(originalText || "", revisedText || "").map((part, index) => {
    if (part.added) {
      return {
        id: `base-${index}`,
        type: "add",
        text: part.value,
        revisedText: part.value
      };
    }

    if (part.removed) {
      return {
        id: `base-${index}`,
        type: "delete",
        text: part.value,
        originalText: part.value
      };
    }

    return {
      id: `base-${index}`,
      type: "equal",
      text: part.value
    };
  });
}

function getOriginalText(op: ReviewChangeOp): string {
  return op.originalText ?? op.text ?? "";
}

function getRevisedText(op: ReviewChangeOp): string {
  return op.revisedText ?? op.text ?? "";
}

function mergePairToReplace(first: ReviewChangeOp, second: ReviewChangeOp, index: number): ReviewChangeOp {
  if (first.type === "delete") {
    return {
      id: `replace-${index}`,
      type: "replace",
      originalText: getOriginalText(first),
      revisedText: getRevisedText(second)
    };
  }

  return {
    id: `replace-${index}`,
    type: "replace",
    originalText: getOriginalText(second),
    revisedText: getRevisedText(first)
  };
}

function mergeAdjacentChanges(ops: ReviewChangeOp[]): ReviewChangeOp[] {
  const result: ReviewChangeOp[] = [];

  for (let i = 0; i < ops.length; i++) {
    const current = ops[i];
    const next = ops[i + 1];

    if (
      next &&
      ((current.type === "delete" && next.type === "add") ||
        (current.type === "add" && next.type === "delete"))
    ) {
      result.push(mergePairToReplace(current, next, i));
      i++;
      continue;
    }

    result.push(current);
  }

  return result;
}

function mergeLocalChangeClusters(ops: ReviewChangeOp[]): ReviewChangeOp[] {
  const result: ReviewChangeOp[] = [];

  for (let i = 0; i < ops.length; i++) {
    const current = ops[i];

    if (current.type === "equal") {
      result.push(current);
      continue;
    }

    const cluster: ReviewChangeOp[] = [];
    let hasAdd = false;
    let hasDelete = false;
    let j = i;

    while (j < ops.length) {
      const item = ops[j];

      if (item.type === "equal" && (item.text || "").length > LOCAL_EQUAL_CONTEXT_LIMIT) {
        break;
      }

      cluster.push(item);
      hasAdd = hasAdd || item.type === "add";
      hasDelete = hasDelete || item.type === "delete";
      j++;

      const next = ops[j];
      if (!next || (next.type === "equal" && (next.text || "").length > LOCAL_EQUAL_CONTEXT_LIMIT)) {
        break;
      }
    }

    if (hasAdd && hasDelete) {
      result.push({
        id: `replace-cluster-${i}`,
        type: "replace",
        originalText: cluster
          .filter((item) => item.type !== "add")
          .map((item) => item.text || item.originalText || "")
          .join(""),
        revisedText: cluster
          .filter((item) => item.type !== "delete")
          .map((item) => item.text || item.revisedText || "")
          .join("")
      });
      i = j - 1;
      continue;
    }

    if (hasAdd) {
      result.push({
        id: `add-cluster-${i}`,
        type: "add",
        text: cluster
          .filter((item) => item.type === "add")
          .map((item) => item.text || item.revisedText || "")
          .join("")
      });
      i = j - 1;
      continue;
    }

    result.push({
      id: `delete-cluster-${i}`,
      type: "delete",
      text: cluster
        .filter((item) => item.type === "delete")
        .map((item) => item.text || item.originalText || "")
        .join("")
    });
    i = j - 1;
  }

  return result;
}

function normalizeFormat(text: string): string {
  return (text || "").replace(FORMAT_REGEX, "");
}

function normalizeWithoutPunctuation(text: string): string {
  return (text || "").replace(PUNCTUATION_REGEX, "");
}

function isFormatOnlyChange(originalText: string, revisedText: string): boolean {
  return Boolean(originalText || revisedText) && normalizeFormat(originalText) === normalizeFormat(revisedText);
}

function isPunctuationOnlyChange(originalText: string, revisedText: string): boolean {
  return (
    Boolean(originalText || revisedText) &&
    normalizeWithoutPunctuation(originalText) === normalizeWithoutPunctuation(revisedText)
  );
}

function getCharSet(text: string): Set<string> {
  return new Set((text || "").replace(/\s/g, "").split("").filter(Boolean));
}

function jaccardSimilarity(a: string, b: string): number {
  const setA = getCharSet(a);
  const setB = getCharSet(b);

  if (setA.size === 0 && setB.size === 0) return 1;
  if (setA.size === 0 || setB.size === 0) return 0;

  const intersection = new Set([...setA].filter((char) => setB.has(char)));
  const union = new Set([...setA, ...setB]);

  return intersection.size / union.size;
}

function getBigrams(text: string): string[] {
  const clean = (text || "").replace(/\s/g, "");
  const result: string[] = [];

  for (let i = 0; i < clean.length - 1; i++) {
    result.push(clean.slice(i, i + 2));
  }

  return result;
}

function ngramOverlapRatio(a: string, b: string): number {
  const aGrams = new Set(getBigrams(a));
  const bGrams = new Set(getBigrams(b));

  if (aGrams.size === 0 || bGrams.size === 0) return 0;

  const intersection = new Set([...aGrams].filter((item) => bGrams.has(item)));
  return intersection.size / Math.min(aGrams.size, bGrams.size);
}

function longestCommonSubstringLength(a: string, b: string): number {
  const left = normalizeWithoutPunctuation(a);
  const right = normalizeWithoutPunctuation(b);
  const dp = Array.from({ length: left.length + 1 }, () => Array(right.length + 1).fill(0));
  let best = 0;

  for (let i = 1; i <= left.length; i++) {
    for (let j = 1; j <= right.length; j++) {
      if (left[i - 1] === right[j - 1]) {
        dp[i][j] = dp[i - 1][j - 1] + 1;
        best = Math.max(best, dp[i][j]);
      }
    }
  }

  return best;
}

function getLengthRatio(originalText: string, revisedText: string): number {
  const maxLen = Math.max(originalText.length, revisedText.length);
  const minLen = Math.min(originalText.length, revisedText.length);
  return maxLen === 0 ? 1 : minLen / maxLen;
}

function containsNewsEntity(text: string): boolean {
  return NEWS_ENTITY_KEYWORDS.some((keyword) => text.includes(keyword));
}

function isRewriteChange(originalText: string, revisedText: string): boolean {
  const similarity = jaccardSimilarity(originalText, revisedText);
  const lengthRatio = getLengthRatio(originalText, revisedText);
  const commonSpan = longestCommonSubstringLength(originalText, revisedText);

  return (
    (similarity >= REWRITE_SIMILARITY_THRESHOLD && lengthRatio >= REWRITE_LENGTH_RATIO_THRESHOLD) ||
    (commonSpan >= 4 && lengthRatio >= 0.3)
  );
}

function isReorderChange(originalText: string, revisedText: string): boolean {
  const charSimilarity = jaccardSimilarity(originalText, revisedText);
  const ngramOverlap = ngramOverlapRatio(originalText, revisedText);
  const lengthRatio = getLengthRatio(originalText, revisedText);
  const entityBoost = containsNewsEntity(originalText) || containsNewsEntity(revisedText);

  return (
    charSimilarity >= (entityBoost ? 0.52 : REORDER_SIMILARITY_THRESHOLD) &&
    ngramOverlap >= (entityBoost ? 0.25 : REORDER_NGRAM_THRESHOLD) &&
    lengthRatio >= REWRITE_LENGTH_RATIO_THRESHOLD
  );
}

function classifyChangeOps(ops: ReviewChangeOp[]): ReviewChangeOp[] {
  return ops.map((op, index) => {
    if (op.type === "add" || op.type === "delete") {
      const text = op.text || op.originalText || op.revisedText || "";

      if (text && normalizeFormat(text) === "") {
        return {
          ...op,
          id: `format-${index}`,
          type: "format",
          originalText: op.type === "delete" ? text : "",
          revisedText: op.type === "add" ? text : "",
          reason: "格式或空格调整",
          confidence: 1
        };
      }

      if (text && normalizeWithoutPunctuation(text) === "") {
        return {
          ...op,
          id: `punctuation-${index}`,
          type: "punctuation",
          originalText: op.type === "delete" ? text : "",
          revisedText: op.type === "add" ? text : "",
          reason: "标点规范化",
          confidence: 1
        };
      }

      return op;
    }

    if (op.type !== "replace") return op;

    const originalText = op.originalText || "";
    const revisedText = op.revisedText || "";
    const similarity = jaccardSimilarity(originalText, revisedText);

    if (isFormatOnlyChange(originalText, revisedText)) {
      return {
        ...op,
        id: `format-${index}`,
        type: "format",
        reason: "格式或空格调整",
        confidence: 1
      };
    }

    if (isPunctuationOnlyChange(originalText, revisedText)) {
      return {
        ...op,
        id: `punctuation-${index}`,
        type: "punctuation",
        reason: "标点或空格规范化",
        confidence: 1
      };
    }

    if (isReorderChange(originalText, revisedText)) {
      return {
        ...op,
        id: `reorder-${index}`,
        type: "reorder",
        reason: "语序调整或信息位置调整",
        confidence: similarity
      };
    }

    if (isRewriteChange(originalText, revisedText)) {
      return {
        ...op,
        id: `rewrite-${index}`,
        type: "rewrite",
        reason: "表达润色，核心含义基本一致",
        confidence: similarity
      };
    }

    return {
      ...op,
      id: `replace-${index}`,
      confidence: similarity
    };
  });
}

function canPairAsMovedChange(deleteOp: ReviewChangeOp, addOp: ReviewChangeOp): boolean {
  const originalText = deleteOp.text || deleteOp.originalText || "";
  const revisedText = addOp.text || addOp.revisedText || "";
  const similarity = jaccardSimilarity(originalText, revisedText);
  const overlap = ngramOverlapRatio(originalText, revisedText);
  const ratio = getLengthRatio(originalText, revisedText);
  const entityBoost = containsNewsEntity(originalText) || containsNewsEntity(revisedText);

  return (
    normalizeWithoutPunctuation(originalText).length >= 4 &&
    normalizeWithoutPunctuation(revisedText).length >= 4 &&
    similarity >= (entityBoost ? 0.48 : REORDER_SIMILARITY_THRESHOLD) &&
    overlap >= (entityBoost ? 0.2 : REORDER_NGRAM_THRESHOLD) &&
    ratio >= 0.35
  );
}

function pairMovedChanges(ops: ReviewChangeOp[]): ReviewChangeOp[] {
  const usedDeletes = new Set<number>();
  const usedAdds = new Set<number>();
  const replacements = new Map<number, ReviewChangeOp>();

  for (let deleteIndex = 0; deleteIndex < ops.length; deleteIndex++) {
    const deleteOp = ops[deleteIndex];
    if (deleteOp.type !== "delete" || usedDeletes.has(deleteIndex)) continue;

    let bestAddIndex = -1;
    let bestScore = 0;

    for (let addIndex = 0; addIndex < ops.length; addIndex++) {
      const addOp = ops[addIndex];
      if (addOp.type !== "add" || usedAdds.has(addIndex)) continue;
      if (!canPairAsMovedChange(deleteOp, addOp)) continue;

      const originalText = deleteOp.text || deleteOp.originalText || "";
      const revisedText = addOp.text || addOp.revisedText || "";
      const score = jaccardSimilarity(originalText, revisedText) + ngramOverlapRatio(originalText, revisedText);

      if (score > bestScore) {
        bestScore = score;
        bestAddIndex = addIndex;
      }
    }

    if (bestAddIndex >= 0) {
      const addOp = ops[bestAddIndex];
      const originalText = deleteOp.text || deleteOp.originalText || "";
      const revisedText = addOp.text || addOp.revisedText || "";

      usedDeletes.add(deleteIndex);
      usedAdds.add(bestAddIndex);
      replacements.set(bestAddIndex, {
        id: `reorder-pair-${deleteIndex}-${bestAddIndex}`,
        type: "reorder",
        originalText,
        revisedText,
        reason: "语序调整或信息位置调整",
        confidence: jaccardSimilarity(originalText, revisedText)
      });
    }
  }

  return ops.flatMap((op, index) => {
    if (usedDeletes.has(index)) return [];
    return [replacements.get(index) || op];
  });
}

export function buildSemanticReviewDiff(originalText: string, revisedText: string): ReviewChangeOp[] {
  const baseOps = buildBaseDiff(originalText, revisedText);
  const clusteredOps = mergeLocalChangeClusters(baseOps);
  const mergedOps = mergeAdjacentChanges(clusteredOps);
  const movedOps = pairMovedChanges(mergedOps);
  return classifyChangeOps(movedOps);
}

export function buildReviewDiff(originalText: string, revisedText: string): ReviewChangeOp[] {
  return buildSemanticReviewDiff(originalText, revisedText);
}

export function getSemanticDiffStats(ops: ReviewChangeOp[]) {
  return {
    addCount: ops.filter((op) => op.type === "add").length,
    deleteCount: ops.filter((op) => op.type === "delete").length,
    replaceCount: ops.filter((op) => op.type === "replace").length,
    rewriteCount: ops.filter((op) => op.type === "rewrite").length,
    reorderCount: ops.filter((op) => op.type === "reorder").length,
    punctuationCount: ops.filter((op) => op.type === "punctuation").length,
    formatCount: ops.filter((op) => op.type === "format").length
  };
}

export function getReviewDiffStats(ops: ReviewChangeOp[]) {
  return getSemanticDiffStats(ops);
}
