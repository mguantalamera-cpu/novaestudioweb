from pathlib import Path

from core.config import TEXT_EXTENSIONS
from core.languages import detect_language
from core.rules import get_builtin_rules
from core.plugins import load_plugins
from core.utils import read_text_file, relative_path, safe_walk
from core.models import ScanResult
from core.tooling import run_external_tools


class Scanner:
    def __init__(self):
        self.rules = get_builtin_rules()
        self.plugins = load_plugins()
        for plugin in self.plugins:
            self.rules.extend(plugin.rules)

    def scan(self, project_path: str, options):
        root = Path(project_path)
        findings = []
        language_stats = {}
        errors = []

        for path in safe_walk(root):
            if path.suffix.lower() not in TEXT_EXTENSIONS:
                continue
            try:
                text = read_text_file(path)
            except Exception as exc:
                errors.append(f"{path}: {exc}")
                continue
            language = detect_language(path)
            language_stats[language] = language_stats.get(language, 0) + 1
            if language == "other":
                continue
            for rule in self.rules:
                if language in rule.languages:
                    findings.extend(rule.scan(relative_path(path, root), text))

        tools_used, tool_findings, tool_errors = run_external_tools(project_path, options)
        findings.extend(tool_findings)
        errors.extend(tool_errors)

        return ScanResult(findings, language_stats, tools_used, errors)
