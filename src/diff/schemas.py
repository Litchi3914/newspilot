from dataclasses import dataclass

@dataclass
class DiffOp:
    type: str
    paragraph_index: int
    original: str
    revised: str
    category: str
    reason: str
    severity: str
