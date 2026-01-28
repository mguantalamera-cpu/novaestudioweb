import json
import shutil
import subprocess
from pathlib import Path

from core.models import Finding, Severity


def _map_severity(value: str) -> Severity:
    mapping = {
        "LOW": Severity.LOW,
        "MEDIUM": Severity.MEDIUM,
        "HIGH": Severity.HIGH,
        "CRITICAL": Severity.CRITICAL,
    }
    return mapping.get(value.upper(), Severity.MEDIUM)


def _run_tool(cmd, cwd):
    try:
        proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=60)
        return proc.returncode, proc.stdout, proc.stderr
    except Exception as exc:
        return 1, "", str(exc)


def run_bandit(project_path: str):
    if not shutil.which("bandit"):
        return [], "bandit not found"
    cmd = ["bandit", "-r", project_path, "-f", "json"]
    code, out, err = _run_tool(cmd, project_path)
    if code != 0:
        return [], err or "bandit failed"
    data = json.loads(out)
    findings = []
    for item in data.get("results", []):
        findings.append(Finding(
            id=f"BANDIT:{item.get('test_id')}",
            title=item.get("test_name", "Bandit finding"),
            description=item.get("issue_text", ""),
            severity=_map_severity(item.get("issue_severity", "MEDIUM")),
            file_path=item.get("filename", ""),
            line=item.get("line_number", 1),
            column=1,
            cwe=item.get("issue_cwe", {}).get("id"),
            owasp=None,
            rule_id=f"BANDIT:{item.get('test_id')}",
            message=item.get("issue_text", ""),
            snippet="",
            fixable=False,
            fixer_id=None,
        ))
    return findings, None


def run_semgrep(project_path: str):
    if not shutil.which("semgrep"):
        return [], "semgrep not found"
    cmd = ["semgrep", "--config=auto", "--json", "--metrics=off", project_path]
    code, out, err = _run_tool(cmd, project_path)
    if code not in (0, 1):
        return [], err or "semgrep failed"
    data = json.loads(out) if out else {}
    findings = []
    for item in data.get("results", []):
        extra = item.get("extra", {})
        findings.append(Finding(
            id=f"SEMGREP:{item.get('check_id')}",
            title=extra.get("message", "Semgrep finding"),
            description=extra.get("message", ""),
            severity=_map_severity(extra.get("severity", "MEDIUM")),
            file_path=item.get("path", ""),
            line=item.get("start", {}).get("line", 1),
            column=item.get("start", {}).get("col", 1),
            cwe=None,
            owasp=None,
            rule_id=f"SEMGREP:{item.get('check_id')}",
            message=extra.get("message", ""),
            snippet="",
            fixable=False,
            fixer_id=None,
        ))
    return findings, None


def run_eslint(project_path: str):
    if not shutil.which("eslint"):
        return [], "eslint not found"
    cmd = ["eslint", "-f", "json", project_path]
    code, out, err = _run_tool(cmd, project_path)
    if code not in (0, 1):
        return [], err or "eslint failed"
    data = json.loads(out) if out else []
    findings = []
    for file_item in data:
        for msg in file_item.get("messages", []):
            findings.append(Finding(
                id=f"ESLINT:{msg.get('ruleId')}",
                title=msg.get("message", "Eslint finding"),
                description=msg.get("message", ""),
                severity=Severity.MEDIUM,
                file_path=file_item.get("filePath", ""),
                line=msg.get("line", 1),
                column=msg.get("column", 1),
                cwe=None,
                owasp=None,
                rule_id=f"ESLINT:{msg.get('ruleId')}",
                message=msg.get("message", ""),
                snippet="",
                fixable=False,
                fixer_id=None,
            ))
    return findings, None


def run_external_tools(project_path: str, options):
    tools_used = []
    findings = []
    errors = []
    if not options.use_external_tools:
        return tools_used, findings, errors

    bandit_findings, bandit_error = run_bandit(project_path)
    if bandit_error:
        errors.append(bandit_error)
    else:
        tools_used.append("bandit")
        findings.extend(bandit_findings)

    semgrep_findings, semgrep_error = run_semgrep(project_path)
    if semgrep_error:
        errors.append(semgrep_error)
    else:
        tools_used.append("semgrep")
        findings.extend(semgrep_findings)

    eslint_findings, eslint_error = run_eslint(project_path)
    if eslint_error:
        errors.append(eslint_error)
    else:
        tools_used.append("eslint")
        findings.extend(eslint_findings)

    return tools_used, findings, errors
