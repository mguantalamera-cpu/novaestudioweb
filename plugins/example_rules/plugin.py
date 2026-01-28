from core.plugins import PluginSpec
from core.models import Finding, Severity
from core.rules.base import Rule


def sample_rule_scan(file_path, text):
    findings = []
    for idx, line in enumerate(text.splitlines(), start=1):
        if "TODO:SECURITY" in line:
            findings.append(Finding(
                id=f"PLG001:{file_path}:{idx}",
                title="Security TODO",
                description="Security TODO marker found",
                severity=Severity.LOW,
                file_path=file_path,
                line=idx,
                column=1,
                cwe=None,
                owasp=None,
                rule_id="PLG001",
                message="TODO:SECURITY marker",
                snippet=line.strip(),
                fixable=False,
                fixer_id=None,
            ))
    return findings


PLUGIN = PluginSpec(
    name="example_rules",
    rules=[
        Rule(
            id="PLG001",
            title="Security TODO",
            description="Security TODO marker",
            severity=Severity.LOW,
            cwe=None,
            owasp=None,
            languages={"python", "javascript"},
            scan=sample_rule_scan,
            message="TODO security marker",
            fixer_id=None,
        )
    ],
    fixers={},
)
