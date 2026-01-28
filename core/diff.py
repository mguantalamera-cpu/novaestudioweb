import difflib
from pathlib import Path


def unified_diff(original_text: str, updated_text: str, file_path: str) -> str:
    original_lines = original_text.splitlines()
    updated_lines = updated_text.splitlines()
    diff_lines = difflib.unified_diff(
        original_lines,
        updated_lines,
        fromfile=f"a/{file_path}",
        tofile=f"b/{file_path}",
        lineterm="",
    )
    return "\n".join(diff_lines)
