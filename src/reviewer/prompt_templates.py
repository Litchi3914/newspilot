def revision_prompt(title: str, text: str, refs: list[dict]) -> str:
    ref_titles='; '.join([r.get('title','') for r in refs[:3]])
    return f"请在不改变事实前提下修订新闻稿。\n标题：{title}\n正文：{text}\n参考：{ref_titles}\n要求缺失信息用【待补充】。"
