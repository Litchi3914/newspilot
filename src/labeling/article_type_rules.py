RULES = {
    "会议新闻": {
        "title": ["召开", "举行", "举办", "座谈", "调研", "研讨会", "交流会", "推进会", "部署会"],
        "body": ["会上", "会议指出", "会议强调", "与会人员"],
    },
    "活动纪实": {
        "title": ["开展", "活动", "比赛", "文化节", "志愿服务", "实践"],
        "body": ["活动现场", "参与者", "志愿者", "同学们"],
    },
    "科研成果": {
        "title": ["发表", "揭示", "发现", "成果", "获批", "项目"],
        "body": ["论文", "期刊", "实验室", "研究表明"],
    },
    "人才培养": {
        "title": ["课程", "教学", "培养", "育人", "实习"],
        "body": ["学生培养", "课程建设", "教学改革"],
    },
    "人物通讯": {
        "title": ["专访", "故事", "风采", "榜样", "校友"],
        "body": ["他说", "她说", "成长经历"],
    },
    "对外交流": {
        "title": ["访问", "合作", "签约", "交流", "国际"],
        "body": ["双方", "合作协议", "来访", "代表团"],
    },
    "评论时评": {
        "title": ["评论", "思考", "观察"],
        "body": [],
    },
    "通知喜报": {
        "title": ["获奖", "入选", "荣获", "名单", "公布", "通知", "公告", "喜报"],
        "body": [],
    },
}


def classify_article(title: str, category: str, body_clean: str) -> dict:
    if category == "狮山时评":
        return {"article_type": "评论时评", "type_confidence": 0.95, "rules_hit": ["category_狮山时评"]}

    best_type = "活动纪实"
    best_score = -1
    best_hits: list[str] = []

    for article_type, conf in RULES.items():
        hits = []
        score = 0
        for kw in conf["title"]:
            if kw in title:
                score += 2
                hits.append(f"title_contains_{kw}")
        for kw in conf["body"]:
            if kw in body_clean:
                score += 1
                hits.append(f"body_contains_{kw}")
        if score > best_score:
            best_score = score
            best_type = article_type
            best_hits = hits

    confidence = 0.5 if best_score <= 0 else min(0.99, 0.55 + best_score * 0.06)
    return {
        "article_type": best_type,
        "type_confidence": round(confidence, 2),
        "rules_hit": best_hits,
    }
