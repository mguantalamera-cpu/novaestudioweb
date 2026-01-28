import re
from core.fixers.base import Fixer, FixResult
from core.models import LineExplanation


class InnerHtmlToTextContentFixer(Fixer):
    def __init__(self):
        super().__init__("JS_FIX_TEXTCONTENT", "Replace innerHTML with textContent for plain text")

    def apply(self, file_path, text):
        lines = text.splitlines()
        explanations = []
        changed = False
        pattern = re.compile(r"(\.innerHTML\s*=\s*)(['\"])([^'\"]*)(\2)")
        for idx, line in enumerate(lines, start=1):
            match = pattern.search(line)
            if not match:
                continue
            content = match.group(3)
            if "<" in content or "&" in content:
                continue
            lines[idx - 1] = line.replace(".innerHTML", ".textContent")
            explanations.append(LineExplanation(
                line=idx,
                content=lines[idx - 1].strip(),
                explanation="Use textContent to avoid HTML injection",
                rule_id="JS003",
            ))
            changed = True
        if not changed:
            return None
        return FixResult("\n".join(lines), explanations)


def get_js_fixers():
    return {
        "JS_FIX_TEXTCONTENT": InnerHtmlToTextContentFixer(),
    }
