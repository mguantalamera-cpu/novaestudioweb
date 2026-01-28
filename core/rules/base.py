from dataclasses import dataclass
from typing import Callable, List, Optional

from core.models import Finding, Severity

ScannerFn = Callable[[str, str], List[Finding]]


@dataclass
class Rule:
    id: str
    title: str
    description: str
    severity: Severity
    cwe: Optional[str]
    owasp: Optional[str]
    languages: set
    scan: ScannerFn
    message: str
    fixer_id: Optional[str]
