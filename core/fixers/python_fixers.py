import re
from core.fixers.base import Fixer, FixResult
from core.models import LineExplanation


class YamlSafeLoadFixer(Fixer):
    def __init__(self):
        super().__init__("PY_FIX_YAML_SAFE_LOAD", "Replace yaml.load with yaml.safe_load")

    def apply(self, file_path, text):
        lines = text.splitlines()
        explanations = []
        changed = False
        for idx, line in enumerate(lines, start=1):
            if "yaml.load" in line and "safe_load" not in line:
                lines[idx - 1] = line.replace("yaml.load", "yaml.safe_load")
                explanations.append(LineExplanation(
                    line=idx,
                    content=lines[idx - 1].strip(),
                    explanation="Use yaml.safe_load to avoid unsafe deserialization",
                    rule_id="PY004",
                ))
                changed = True
        if not changed:
            return None
        return FixResult("\n".join(lines), explanations)


class RequestsVerifyFixer(Fixer):
    def __init__(self):
        super().__init__("PY_FIX_VERIFY_TRUE", "Enable TLS verification")

    def apply(self, file_path, text):
        lines = text.splitlines()
        explanations = []
        changed = False
        pattern = re.compile(r"verify\s*=\s*False")
        for idx, line in enumerate(lines, start=1):
            if pattern.search(line):
                lines[idx - 1] = pattern.sub("verify=True", line)
                explanations.append(LineExplanation(
                    line=idx,
                    content=lines[idx - 1].strip(),
                    explanation="Enable TLS verification for requests",
                    rule_id="PY007",
                ))
                changed = True
        if not changed:
            return None
        return FixResult("\n".join(lines), explanations)


class SubprocessShellFixer(Fixer):
    def __init__(self):
        super().__init__("PY_FIX_SHELL_FALSE", "Disable shell=True when list args are used")

    def apply(self, file_path, text):
        lines = text.splitlines()
        explanations = []
        changed = False
        for idx, line in enumerate(lines, start=1):
            if "subprocess." in line and "shell=True" in line and "[" in line:
                lines[idx - 1] = line.replace("shell=True", "shell=False")
                explanations.append(LineExplanation(
                    line=idx,
                    content=lines[idx - 1].strip(),
                    explanation="Disable shell execution when arguments are a list",
                    rule_id="PY001",
                ))
                changed = True
        if not changed:
            return None
        return FixResult("\n".join(lines), explanations)


def get_python_fixers():
    return {
        "PY_FIX_YAML_SAFE_LOAD": YamlSafeLoadFixer(),
        "PY_FIX_VERIFY_TRUE": RequestsVerifyFixer(),
        "PY_FIX_SHELL_FALSE": SubprocessShellFixer(),
    }
