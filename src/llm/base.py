from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class BaseLLMClient(ABC):
    @abstractmethod
    def classify_article_type(self, title: str, draft_text: str, candidate_types: Optional[List[str]] = None) -> Dict[str, Any]:
        pass

    @abstractmethod
    def review_article(self, title: str, draft_text: str, article_type: str, references: Optional[List[Dict[str, Any]]] = None, rule_check_result: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        pass

    @abstractmethod
    def revise_article(self, title: str, draft_text: str, article_type: str, references: Optional[List[Dict[str, Any]]] = None, issues: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        pass
