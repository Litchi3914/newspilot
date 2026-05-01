from __future__ import annotations

import difflib
import re

from src.review.models import DisplayMode, EditOperation, EditType, Severity

PUNCT_RE = re.compile(r"[，。！？；：“”‘’、,.!?;:\"'\s]")
ENTITY_KEYWORDS = ("会议", "活动", "交流会", "座谈会", "研讨会", "工作室", "学院", "本科生院", "水产楼")


def _strip_punct(text: str) -> str:
    return PUNCT_RE.sub("", text or "")


def _char_similarity(a: str, b: str) -> float:
    sa = set((a or "").replace(" ", ""))
    sb = set((b or "").replace(" ", ""))
    if not sa and not sb:
        return 1.0
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def _bigrams(text: str) -> set[str]:
    clean = _strip_punct(text)
    return {clean[i : i + 2] for i in range(max(0, len(clean) - 1))}


def _ngram_overlap(a: str, b: str) -> float:
    ga = _bigrams(a)
    gb = _bigrams(b)
    if not ga or not gb:
        return 0.0
    return len(ga & gb) / min(len(ga), len(gb))


def _length_ratio(a: str, b: str) -> float:
    mx = max(len(a or ""), len(b or ""))
    mn = min(len(a or ""), len(b or ""))
    return 1.0 if mx == 0 else mn / mx


def _contains_entity(text: str) -> bool:
    return any(k in (text or "") for k in ENTITY_KEYWORDS)


def _classify_replace(source: str, target: str) -> tuple[EditType, DisplayMode, str, Severity, float]:
    similarity = _char_similarity(source, target)
    if source.replace(" ", "") == target.replace(" ", ""):
        return EditType.PUNCTUATION, DisplayMode.REPLACE, "格式或空格调整。", Severity.LOW, 1.0
    if _strip_punct(source) == _strip_punct(target):
        return EditType.PUNCTUATION, DisplayMode.REPLACE, "标点或空格规范化。", Severity.LOW, 1.0
    entity = _contains_entity(source) or _contains_entity(target)
    if similarity >= (0.5 if entity else 0.6) and _ngram_overlap(source, target) >= (0.2 if entity else 0.35):
        return EditType.REORDER, DisplayMode.SEMANTIC_REPLACE, "语序调整或信息位置调整。", Severity.MEDIUM if entity else Severity.LOW, similarity
    if similarity >= 0.55 and _length_ratio(source, target) >= 0.35:
        return EditType.WORDING, DisplayMode.SEMANTIC_REPLACE, "表达润色，核心含义基本一致。", Severity.LOW, similarity
    return EditType.WORDING, DisplayMode.REPLACE, "局部内容替换。", Severity.MEDIUM if entity else Severity.LOW, similarity


def _op(
    index: int,
    edit_type: EditType,
    source: str,
    target: str,
    reason: str,
    display_mode: DisplayMode,
    risk: Severity = Severity.LOW,
    confidence: float = 0.8,
    start: int | None = None,
    end: int | None = None,
) -> EditOperation:
    return EditOperation(
        id=f"edit_{index:03d}",
        type=edit_type,
        source_text=source,
        target_text=target,
        reason=reason,
        confidence=round(confidence, 3),
        display_mode=display_mode,
        risk_level=risk,
        start_char=start,
        end_char=end,
    )


def build_semantic_diff(
    source_text: str,
    revised_text: str,
    llm_edit_operations: list[dict] | None = None,
) -> list[EditOperation]:
    if source_text == revised_text:
        return []

    matcher = difflib.SequenceMatcher(a=source_text or "", b=revised_text or "")
    edits: list[EditOperation] = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        source = (source_text or "")[i1:i2]
        target = (revised_text or "")[j1:j2]
        idx = len(edits) + 1
        if tag == "insert":
            if target and not _strip_punct(target):
                edits.append(_op(idx, EditType.PUNCTUATION, "", target, "标点规范化。", DisplayMode.REPLACE, Severity.LOW, 1.0, i1, i2))
            else:
                edits.append(_op(idx, EditType.ADD, "", target, "补充必要信息或衔接表达。", DisplayMode.INSERT, Severity.MEDIUM, 0.75, i1, i2))
        elif tag == "delete":
            if source and not _strip_punct(source):
                edits.append(_op(idx, EditType.PUNCTUATION, source, "", "标点规范化。", DisplayMode.REPLACE, Severity.LOW, 1.0, i1, i2))
            else:
                edits.append(_op(idx, EditType.DELETE, source, "", "删除冗余或不适合新闻稿的表达。", DisplayMode.DELETE, Severity.LOW, 0.75, i1, i2))
        else:
            edit_type, display, reason, risk, confidence = _classify_replace(source, target)
            edits.append(_op(idx, edit_type, source, target, reason, display, risk, confidence, i1, i2))

    return _merge_tiny_edits(_pair_moved_edits(edits))


def _can_pair_as_reorder(delete_edit: EditOperation, add_edit: EditOperation) -> bool:
    source = delete_edit.source_text
    target = add_edit.target_text
    if _strip_punct(source) == _strip_punct(target) and len(_strip_punct(source)) >= 2:
        return True
    if len(_strip_punct(source)) < 4 or len(_strip_punct(target)) < 4:
        return False
    entity = _contains_entity(source) or _contains_entity(target)
    return (
        _char_similarity(source, target) >= (0.45 if entity else 0.6)
        and _ngram_overlap(source, target) >= (0.18 if entity else 0.35)
        and _length_ratio(source, target) >= 0.3
    )


def _pair_moved_edits(edits: list[EditOperation]) -> list[EditOperation]:
    used_deletes: set[int] = set()
    used_adds: set[int] = set()
    replacements: dict[int, EditOperation] = {}

    for delete_idx, delete_edit in enumerate(edits):
        if delete_edit.type != EditType.DELETE or delete_idx in used_deletes:
            continue
        best_idx = -1
        best_score = 0.0
        for add_idx, add_edit in enumerate(edits):
            if add_edit.type != EditType.ADD or add_idx in used_adds:
                continue
            if not _can_pair_as_reorder(delete_edit, add_edit):
                continue
            score = _char_similarity(delete_edit.source_text, add_edit.target_text) + _ngram_overlap(delete_edit.source_text, add_edit.target_text)
            if score > best_score:
                best_score = score
                best_idx = add_idx
        if best_idx >= 0:
            add_edit = edits[best_idx]
            used_deletes.add(delete_idx)
            used_adds.add(best_idx)
            replacements[best_idx] = _op(
                best_idx + 1,
                EditType.REORDER,
                delete_edit.source_text,
                add_edit.target_text,
                "语序调整或信息位置调整。",
                DisplayMode.SEMANTIC_REPLACE,
                Severity.MEDIUM,
                _char_similarity(delete_edit.source_text, add_edit.target_text),
                delete_edit.start_char,
                add_edit.end_char,
            )

    result: list[EditOperation] = []
    for idx, edit in enumerate(edits):
        if idx in used_deletes:
            continue
        result.append(replacements.get(idx, edit))
    return [edit.model_copy(update={"id": f"edit_{i:03d}"}) for i, edit in enumerate(result, start=1)]


def _merge_tiny_edits(edits: list[EditOperation]) -> list[EditOperation]:
    if not edits:
        return []
    merged: list[EditOperation] = []
    buffer: list[EditOperation] = []
    for edit in edits:
        short = len(edit.source_text) + len(edit.target_text) <= 6
        if short and edit.type in {EditType.PUNCTUATION, EditType.WORDING}:
            buffer.append(edit)
            continue
        if buffer:
            merged.append(_merge_buffer(buffer, len(merged) + 1))
            buffer = []
        merged.append(edit.model_copy(update={"id": f"edit_{len(merged) + 1:03d}"}))
    if buffer:
        merged.append(_merge_buffer(buffer, len(merged) + 1))
    return merged


def _merge_buffer(buffer: list[EditOperation], index: int) -> EditOperation:
    source = "".join(x.source_text for x in buffer)
    target = "".join(x.target_text for x in buffer)
    edit_type, display, reason, risk, confidence = _classify_replace(source, target)
    return _op(index, edit_type, source, target, reason, display, risk, confidence, buffer[0].start_char, buffer[-1].end_char)
