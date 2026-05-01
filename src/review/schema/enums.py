from enum import Enum

class IssueType(str, Enum):
    political_safety = 'political_safety'
    factual_accuracy = 'factual_accuracy'
    style = 'style'
    grammar = 'grammar'
    structure = 'structure'
    title = 'title'
    source_attribution = 'source_attribution'
    format = 'format'
    other = 'other'

class Severity(str, Enum):
    low = 'low'
    medium = 'medium'
    high = 'high'
    critical = 'critical'

class DiffType(str, Enum):
    insert = 'insert'
    delete = 'delete'
    replace = 'replace'
    equal = 'equal'
    comment = 'comment'
    warning = 'warning'

class RiskLevel(str, Enum):
    low = 'low'
    medium = 'medium'
    high = 'high'
    critical = 'critical'
