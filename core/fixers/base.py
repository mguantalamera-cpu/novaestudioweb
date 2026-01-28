from dataclasses import dataclass
from typing import Optional, List

from core.models import LineExplanation


@dataclass
class FixResult:
    updated_text: str
    explanations: List[LineExplanation]


class Fixer:
    def __init__(self, fixer_id: str, description: str, touches_logic: bool = False):
        self.fixer_id = fixer_id
        self.description = description
        self.touches_logic = touches_logic

    def apply(self, file_path: str, text: str) -> Optional[FixResult]:
        raise NotImplementedError
