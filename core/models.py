from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Finding:
    id: str
    title: str
    description: str
    severity: Severity
    file_path: str
    line: int
    column: int
    cwe: Optional[str]
    owasp: Optional[str]
    rule_id: str
    message: str
    snippet: str
    fixable: bool
    fixer_id: Optional[str]


@dataclass
class LineExplanation:
    line: int
    content: str
    explanation: str
    rule_id: str


@dataclass
class FileChange:
    file_path: str
    original_text: str
    updated_text: str
    original_hash: str
    line_explanations: List[LineExplanation] = field(default_factory=list)
    applied_rules: List[str] = field(default_factory=list)


@dataclass
class ScanResult:
    findings: List[Finding]
    language_stats: dict
    tools_used: List[str]
    errors: List[str]


@dataclass
class PatchPlan:
    file_changes: List[FileChange]
    diff: str
    skipped: List[str]


@dataclass
class PatchResult:
    applied_files: List[str]
    backups: List[str]
    errors: List[str]


@dataclass
class ReportPaths:
    output_dir: str
    markdown_path: str
    html_path: str
    json_path: str
    changelog_path: str
