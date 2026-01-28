import re
from core.models import Finding, Severity
from core.rules.base import Rule


def _make_finding(rule, file_path, line_no, line, message, fixable, fixer_id):
    return Finding(
        id=f"{rule.id}:{file_path}:{line_no}",
        title=rule.title,
        description=rule.description,
        severity=rule.severity,
        file_path=file_path,
        line=line_no,
        column=1,
        cwe=rule.cwe,
        owasp=rule.owasp,
        rule_id=rule.id,
        message=message,
        snippet=line.strip(),
        fixable=fixable,
        fixer_id=fixer_id,
    )


def _scan_line_regex(rule, file_path, text, pattern, message, fixable, fixer_id):
    findings = []
    for idx, line in enumerate(text.splitlines(), start=1):
        if pattern.search(line):
            findings.append(_make_finding(rule, file_path, idx, line, message, fixable, fixer_id))
    return findings


def get_python_rules():
    rules = []

    def subprocess_shell_scan(file_path, text):
        pattern = re.compile(r"subprocess\.(run|Popen|call)\s*\(.*shell\s*=\s*True")
        return _scan_line_regex(
            rules[0], file_path, text, pattern,
            "shell=True enables command injection risk",
            True, "PY_FIX_SHELL_FALSE"
        )

    def os_system_scan(file_path, text):
        pattern = re.compile(r"os\.system\s*\(")
        return _scan_line_regex(
            rules[1], file_path, text, pattern,
            "os.system executes via shell",
            False, None
        )

    def random_token_scan(file_path, text):
        pattern = re.compile(r"random\.(choice|randint|randrange)")
        findings = []
        for idx, line in enumerate(text.splitlines(), start=1):
            if pattern.search(line) and re.search(r"token|secret|key|password", line, re.IGNORECASE):
                findings.append(_make_finding(rules[2], file_path, idx, line, "Use secrets for tokens", False, None))
        return findings

    def yaml_load_scan(file_path, text):
        pattern = re.compile(r"yaml\.load\s*\(")
        return _scan_line_regex(
            rules[3], file_path, text, pattern,
            "yaml.load is unsafe without SafeLoader",
            True, "PY_FIX_YAML_SAFE_LOAD"
        )

    def hardcoded_secret_scan(file_path, text):
        secret_patterns = [
            re.compile(r"AKIA[0-9A-Z]{16}"),
            re.compile(r"sk_live_[0-9a-zA-Z]{16,}"),
            re.compile(r"AIza[0-9A-Za-z\-_]{30,}"),
            re.compile(r"-----BEGIN PRIVATE KEY-----"),
            re.compile(r"password\s*=\s*['\"]")
        ]
        findings = []
        for idx, line in enumerate(text.splitlines(), start=1):
            if any(p.search(line) for p in secret_patterns):
                findings.append(_make_finding(rules[4], file_path, idx, line, "Hardcoded secret detected", False, None))
        return findings

    def sql_injection_scan(file_path, text):
        pattern = re.compile(r"\.execute\s*\(.*(\+|%|\{)")
        return _scan_line_regex(
            rules[5], file_path, text, pattern,
            "Possible SQL injection via string concatenation", False, None
        )

    def requests_verify_scan(file_path, text):
        pattern = re.compile(r"verify\s*=\s*False")
        return _scan_line_regex(
            rules[6], file_path, text, pattern,
            "TLS verification disabled", True, "PY_FIX_VERIFY_TRUE"
        )

    def pickle_load_scan(file_path, text):
        pattern = re.compile(r"pickle\.(loads|load)\s*\(")
        return _scan_line_regex(
            rules[7], file_path, text, pattern,
            "pickle is unsafe for untrusted data", False, None
        )

    rules.append(Rule(
        id="PY001",
        title="subprocess shell=True",
        description="Avoid shell=True when possible",
        severity=Severity.HIGH,
        cwe="CWE-78",
        owasp="A03:2021",
        languages={"python"},
        scan=subprocess_shell_scan,
        message="shell=True enables command injection",
        fixer_id="PY_FIX_SHELL_FALSE",
    ))
    rules.append(Rule(
        id="PY002",
        title="os.system usage",
        description="os.system executes via shell",
        severity=Severity.HIGH,
        cwe="CWE-78",
        owasp="A03:2021",
        languages={"python"},
        scan=os_system_scan,
        message="os.system is risky",
        fixer_id=None,
    ))
    rules.append(Rule(
        id="PY003",
        title="random for tokens",
        description="random is not suitable for secrets",
        severity=Severity.MEDIUM,
        cwe="CWE-338",
        owasp="A02:2021",
        languages={"python"},
        scan=random_token_scan,
        message="Use secrets for tokens",
        fixer_id=None,
    ))
    rules.append(Rule(
        id="PY004",
        title="yaml.load unsafe",
        description="Use yaml.safe_load",
        severity=Severity.HIGH,
        cwe="CWE-502",
        owasp="A08:2021",
        languages={"python"},
        scan=yaml_load_scan,
        message="yaml.load is unsafe",
        fixer_id="PY_FIX_YAML_SAFE_LOAD",
    ))
    rules.append(Rule(
        id="PY005",
        title="hardcoded secret",
        description="Avoid embedding secrets in code",
        severity=Severity.CRITICAL,
        cwe="CWE-798",
        owasp="A02:2021",
        languages={"python"},
        scan=hardcoded_secret_scan,
        message="Hardcoded secret",
        fixer_id=None,
    ))
    rules.append(Rule(
        id="PY006",
        title="sql injection",
        description="Use parameterized queries",
        severity=Severity.HIGH,
        cwe="CWE-89",
        owasp="A03:2021",
        languages={"python"},
        scan=sql_injection_scan,
        message="Possible SQL injection",
        fixer_id=None,
    ))
    rules.append(Rule(
        id="PY007",
        title="requests verify disabled",
        description="TLS verification disabled",
        severity=Severity.MEDIUM,
        cwe="CWE-295",
        owasp="A07:2021",
        languages={"python"},
        scan=requests_verify_scan,
        message="verify=False disables TLS validation",
        fixer_id="PY_FIX_VERIFY_TRUE",
    ))
    rules.append(Rule(
        id="PY008",
        title="pickle load",
        description="Avoid pickle with untrusted data",
        severity=Severity.HIGH,
        cwe="CWE-502",
        owasp="A08:2021",
        languages={"python"},
        scan=pickle_load_scan,
        message="pickle loads untrusted data",
        fixer_id=None,
    ))

    return rules
