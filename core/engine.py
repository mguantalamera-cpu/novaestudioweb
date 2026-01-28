from pathlib import Path
from core.scanner import Scanner
from core.fixers import get_all_fixers
from core.diff import unified_diff
from core.utils import hash_text, read_text_file
from core.models import PatchPlan, PatchResult, FileChange
from core.report import write_reports


class ScanEngine:
    def __init__(self):
        self.scanner = Scanner()
        self.fixers = get_all_fixers()
        self.project_root = None

    def scan_project(self, project_path: str, options):
        self.project_root = Path(project_path).resolve()
        return self.scanner.scan(project_path, options)

    def _resolve_path(self, rel_path: str) -> Path:
        if self.project_root:
            return (self.project_root / rel_path).resolve()
        return Path(rel_path).resolve()

    def generate_patch(self, scan_result, options):
        if options.no_auto_fix:
            return PatchPlan([], "", ["Auto-fix disabled"])

        file_changes = []
        skipped = []
        file_cache = {}

        for finding in scan_result.findings:
            if not finding.fixable or not finding.fixer_id:
                continue
            fixer = self.fixers.get(finding.fixer_id)
            if not fixer:
                skipped.append(f"No fixer for {finding.rule_id}")
                continue
            if options.no_touch_business_logic and fixer.touches_logic:
                skipped.append(f"Skipped {finding.rule_id} due to no-touch-business-logic")
                continue

            rel_path = finding.file_path
            full_path = self._resolve_path(rel_path)
            if rel_path not in file_cache:
                try:
                    original_text = read_text_file(full_path)
                except Exception as exc:
                    skipped.append(f"{finding.file_path}: {exc}")
                    continue
                file_cache[rel_path] = {
                    "original": original_text,
                    "current": original_text,
                    "explanations": [],
                    "rules": [],
                }

            current_text = file_cache[rel_path]["current"]
            result = fixer.apply(rel_path, current_text)
            if not result:
                skipped.append(f"Fixer {finding.fixer_id} skipped for {finding.file_path}")
                continue
            file_cache[rel_path]["current"] = result.updated_text
            file_cache[rel_path]["explanations"].extend(result.explanations)
            file_cache[rel_path]["rules"].append(finding.rule_id)

        diff_chunks = []
        for rel_path, data in file_cache.items():
            if data["current"] == data["original"]:
                continue
            diff_chunks.append(unified_diff(data["original"], data["current"], rel_path))
            file_changes.append(FileChange(
                file_path=rel_path,
                original_text=data["original"],
                updated_text=data["current"],
                original_hash=hash_text(data["original"]),
                line_explanations=data["explanations"],
                applied_rules=data["rules"],
            ))

        return PatchPlan(file_changes=file_changes, diff="\n".join(diff_chunks), skipped=skipped)

    def apply_patch(self, patch_plan, create_backup: bool):
        applied = []
        backups = []
        errors = []
        backup_root = (self.project_root or Path(".")).resolve() / ".backup"

        for change in patch_plan.file_changes:
            full_path = self._resolve_path(change.file_path)
            try:
                current_text = read_text_file(full_path)
            except Exception as exc:
                errors.append(f"{change.file_path}: {exc}")
                continue
            if hash_text(current_text) != change.original_hash:
                errors.append(f"{change.file_path}: file changed since scan")
                continue

            if create_backup:
                backup_root.mkdir(parents=True, exist_ok=True)
                safe_name = change.file_path.replace("/", "_").replace("\\", "_")
                backup_path = backup_root / (safe_name + ".bak")
                backup_path.write_text(current_text, encoding="utf-8")
                backups.append(str(backup_path))

            full_path.write_text(change.updated_text, encoding="utf-8")
            applied.append(change.file_path)

        return PatchResult(applied_files=applied, backups=backups, errors=errors)

    def export_report(self, project_path: str, scan_result, patch_plan, patch_result):
        return write_reports(project_path, scan_result, patch_plan, patch_result)
