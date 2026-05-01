from dataclasses import dataclass

@dataclass
class ReviewIssue:
    category: str
    severity: str
    problem: str
    suggestion: str
