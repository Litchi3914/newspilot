def classify_prompt(title: str, draft_text: str, candidate_types: list[str]) -> str:
    return f"你是一名高校新闻稿编辑。请判断以下稿件类型。可选类型：{','.join(candidate_types)}。只输出JSON。\n标题：{title}\n正文：{draft_text}"

def review_prompt(title: str, draft_text: str, article_type: str, rule_check_result: dict | None, references: list[dict] | None) -> str:
    return (
        "你是高校新闻稿审稿助手。请只输出合法 JSON，不要输出 Markdown 或解释文字。"
        "任务：输出可解释、可追踪、可人工核验的结构化审稿结果。"
        "必须包含 detected_type、review_summary、issues、revised_title、revised_text、fact_risks。"
        "原则：不得擅自修改人名、单位、职务、时间、地点、会议名称、活动名称、数字、奖项、引用语等事实项；"
        "如发现事实风险，只能写入 fact_risks 或 issues，提示人工核验。\n"
        f"类型：{article_type}\n标题：{title}\n正文：{draft_text}\n规则结果：{rule_check_result}\n参考：{references}"
    )

def revise_prompt(title: str, draft_text: str, article_type: str, issues: list[dict] | None, references: list[dict] | None) -> str:
    return (
        "请在不改变事实项的前提下修订高校新闻稿，并只输出合法 JSON。"
        "必须包含 revised_title、revised_text、issues、fact_risks。"
        "事实项包括人名、单位、职务、时间、地点、会议/活动名称、数字、奖项、引用语；"
        "这些内容不得凭空替换，需核验时写入 fact_risks。\n"
        f"类型：{article_type}\n标题：{title}\n正文：{draft_text}\n问题：{issues}\n参考：{references}"
    )
