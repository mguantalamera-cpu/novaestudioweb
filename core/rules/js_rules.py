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


def get_js_rules():
    rules = []

    def eval_scan(file_path, text):
        pattern = re.compile(r"\beval\s*\(")
        return _scan_line_regex(rules[0], file_path, text, pattern, "eval is dangerous", False, None)

    def function_scan(file_path, text):
        pattern = re.compile(r"new\s+Function\s*\(")
        return _scan_line_regex(rules[1], file_path, text, pattern, "Function constructor is dangerous", False, None)

    def inner_html_scan(file_path, text):
        pattern = re.compile(r"\.innerHTML\s*=")
        return _scan_line_regex(rules[2], file_path, text, pattern, "innerHTML can enable XSS", True, "JS_FIX_TEXTCONTENT")

    def hardcoded_secret_scan(file_path, text):
        secret_patterns = [
            re.compile(r"sk_live_[0-9a-zA-Z]{16,}"),
            re.compile(r"AIza[0-9A-Za-z\-_]{30,}"),
            re.compile(r"-----BEGIN PRIVATE KEY-----"),
            re.compile(r"password\s*[:=]\s*['\"]")
        ]
        findings = []
        for idx, line in enumerate(text.splitlines(), start=1):
            if any(p.search(line) for p in secret_patterns):
                findings.append(_make_finding(rules[3], file_path, idx, line, "Hardcoded secret detected", False, None))
        return findings

    def math_random_scan(file_path, text):
        pattern = re.compile(r"Math\.random\s*\(")
        return _scan_line_regex(rules[4], file_path, text, pattern, "Math.random is not secure", False, None)

    def sql_concat_scan(file_path, text):
        pattern = re.compile(r"query\s*\(.*\+")
        return _scan_line_regex(rules[5], file_path, text, pattern, "Possible SQL injection", False, None)

    def document_write_scan(file_path, text):
        pattern = re.compile(r"document\.write\s*\(")
        return _scan_line_regex(rules[6], file_path, text, pattern, "document.write can enable XSS", False, None)

    def child_process_exec_scan(file_path, text):
        pattern = re.compile(r"child_process\.exec\s*\(")
        return _scan_line_regex(rules[7], file_path, text, pattern, "exec with shell is risky", False, None)

    rules.append(Rule(
        id="JS001",
        title="eval usage",
        description="Avoid eval",
        severity=Severity.HIGH,
        cwe="CWE-95",
        owasp="A03:2021",
        languages={"javascript"},
        scan=eval_scan,
        message="eval is dangerous",
        fixer_id=None,
    ))
    rules.append(Rule(
        id="JS002",
        title="Function constructor",
        description="Avoid new Function",
        severity=Severity.HIGH,
        cwe="CWE-95",
        owasp="A03:2021",
        languages={"javascript"},
        scan=function_scan,
        message="Function constructor is dangerous",
        fixer_id=None,
    ))
    rules.append(Rule(
        id="JS003",
        title="innerHTML assignment",
        description="Use textContent or sanitize",
        severity=Severity.MEDIUM,
        cwe="CWE-79",
        owasp="A03:2021",
        languages={"javascript"},
        scan=inner_html_scan,
        message="innerHTML can enable XSS",
        fixer_id="JS_FIX_TEXTCONTENT",
    ))
    rules.append(Rule(
        id="JS004",
        title="hardcoded secret",
        description="Avoid embedding secrets in code",
        severity=Severity.CRITICAL,
        cwe="CWE-798",
        owasp="A02:2021",
        languages={"javascript"},
        scan=hardcoded_secret_scan,
        message="Hardcoded secret",
        fixer_id=None,
    ))
    rules.append(Rule(
        id="JS005",
        title="Math.random for tokens",
        description="Use crypto API",
        severity=Severity.MEDIUM,
        cwe="CWE-338",
        owasp="A02:2021",
        languages={"javascript"},
        scan=math_random_scan,
        message="Math.random is not secure",
        fixer_id=None,
    ))
    rules.append(Rule(
        id="JS006",
        title="SQL injection",
        description="Avoid string concatenation in queries",
        severity=Severity.HIGH,
        cwe="CWE-89",
        owasp="A03:2021",
        languages={"javascript"},
        scan=sql_concat_scan,
        message="Possible SQL injection",
        fixer_id=None,
    ))
    rules.append(Rule(
        id="JS007",
        title="document.write usage",
        description="document.write can enable XSS",
        severity=Severity.MEDIUM,
        cwe="CWE-79",
        owasp="A03:2021",
        languages={"javascript"},
        scan=document_write_scan,
        message="document.write is risky",
        fixer_id=None,
    ))
    rules.append(Rule(
        id="JS008",
        title="child_process exec",
        description="exec uses a shell",
        severity=Severity.HIGH,
        cwe="CWE-78",
        owasp="A03:2021",
        languages={"javascript"},
        scan=child_process_exec_scan,
        message="child_process.exec is risky",
        fixer_id=None,
    ))

    return rules
