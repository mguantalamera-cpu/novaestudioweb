import json
from datetime import datetime
from pathlib import Path

from core.models import ReportPaths


def _severity_counts(findings):
    counts = {"low": 0, "medium": 0, "high": 0, "critical": 0}
    for f in findings:
        counts[f.severity.value] = counts.get(f.severity.value, 0) + 1
    return counts


def _finding_to_dict(finding):
    return {
        "id": finding.id,
        "title": finding.title,
        "description": finding.description,
        "severity": finding.severity.value,
        "file_path": finding.file_path,
        "line": finding.line,
        "column": finding.column,
        "cwe": finding.cwe,
        "owasp": finding.owasp,
        "rule_id": finding.rule_id,
        "message": finding.message,
        "snippet": finding.snippet,
        "fixable": finding.fixable,
        "fixer_id": finding.fixer_id,
    }


def _explanations_by_file(file_changes):
    data = {}
    for change in file_changes:
        data.setdefault(change.file_path, [])
        for exp in change.line_explanations:
            data[change.file_path].append({
                "line": exp.line,
                "content": exp.content,
                "explanation": exp.explanation,
                "rule": exp.rule_id,
            })
    return data


def write_reports(project_path: str, scan_result, patch_plan, patch_result):
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(project_path) / "reports" / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)

    summary = {
        "findings": len(scan_result.findings),
        "severity": _severity_counts(scan_result.findings),
        "languages": scan_result.language_stats,
        "tools": scan_result.tools_used,
        "errors": scan_result.errors,
    }

    explanations = _explanations_by_file(patch_plan.file_changes if patch_plan else [])

    json_report = {
        "summary": summary,
        "findings": [_finding_to_dict(f) for f in scan_result.findings],
        "patch": {
            "diff": patch_plan.diff if patch_plan else "",
            "applied": patch_result.applied_files if patch_result else [],
            "backups": patch_result.backups if patch_result else [],
            "errors": patch_result.errors if patch_result else [],
            "line_explanations": explanations,
        },
    }

    markdown_lines = []
    markdown_lines.append("# Security Scan Report")
    markdown_lines.append("")
    markdown_lines.append(f"Generated: {timestamp} UTC")
    markdown_lines.append("")
    markdown_lines.append("## Summary")
    markdown_lines.append(f"Findings: {summary['findings']}")
    markdown_lines.append("")
    markdown_lines.append("| Severity | Count |")
    markdown_lines.append("| --- | --- |")
    for sev, count in summary["severity"].items():
        markdown_lines.append(f"| {sev} | {count} |")
    markdown_lines.append("")
    markdown_lines.append(f"Languages: {summary['languages']}")
    markdown_lines.append(f"Tools: {summary['tools']}")
    markdown_lines.append("")
    markdown_lines.append("## Findings")
    for f in scan_result.findings:
        markdown_lines.append(f"- [{f.severity.value}] {f.rule_id} {f.file_path}:{f.line} - {f.message}")
    markdown_lines.append("")
    markdown_lines.append("## Applied Changes")
    if patch_plan and patch_plan.file_changes:
        markdown_lines.append("```diff")
        markdown_lines.append(patch_plan.diff)
        markdown_lines.append("```")
    else:
        markdown_lines.append("No changes applied")
    markdown_lines.append("")
    markdown_lines.append("## Line by Line Explanation")
    if explanations:
        for file_path, items in explanations.items():
            markdown_lines.append(f"### {file_path}")
            for item in items:
                markdown_lines.append(f"- L{item['line']}: `{item['content']}` - {item['explanation']} ({item['rule']})")
    else:
        markdown_lines.append("No line changes")

    html_lines = []
    html_lines.append("<html><head><meta charset='utf-8'><title>Security Report</title></head><body>")
    html_lines.append("<h1>Security Scan Report</h1>")
    html_lines.append(f"<p>Generated: {timestamp} UTC</p>")
    html_lines.append("<h2>Summary</h2>")
    html_lines.append(f"<pre>{json.dumps(summary, indent=2)}</pre>")
    html_lines.append("<h2>Findings</h2><ul>")
    for f in scan_result.findings:
        html_lines.append(f"<li>[{f.severity.value}] {f.rule_id} {f.file_path}:{f.line} - {f.message}</li>")
    html_lines.append("</ul>")
    html_lines.append("<h2>Applied Changes</h2>")
    html_lines.append("<pre>")
    html_lines.append(patch_plan.diff if patch_plan else "")
    html_lines.append("</pre>")
    html_lines.append("<h2>Line by Line Explanation</h2>")
    for file_path, items in explanations.items():
        html_lines.append(f"<h3>{file_path}</h3><ul>")
        for item in items:
            html_lines.append(f"<li>L{item['line']}: <code>{item['content']}</code> - {item['explanation']} ({item['rule']})</li>")
        html_lines.append("</ul>")
    html_lines.append("</body></html>")

    md_path = output_dir / "report.md"
    html_path = output_dir / "report.html"
    json_path = output_dir / "report.json"
    changelog_path = output_dir / "CHANGELOG_SECURITY.md"

    md_path.write_text("\n".join(markdown_lines), encoding="utf-8")
    html_path.write_text("\n".join(html_lines), encoding="utf-8")
    json_path.write_text(json.dumps(json_report, indent=2), encoding="utf-8")

    changelog_lines = [
        f"# Security Changelog {timestamp}",
        "",
        f"Findings: {summary['findings']}",
        f"Applied files: {patch_result.applied_files if patch_result else []}",
        "",
    ]
    changelog_path.write_text("\n".join(changelog_lines), encoding="utf-8")

    return ReportPaths(
        output_dir=str(output_dir),
        markdown_path=str(md_path),
        html_path=str(html_path),
        json_path=str(json_path),
        changelog_path=str(changelog_path),
    )
