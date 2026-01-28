from pathlib import Path
from core.config import PY_EXTENSIONS, JS_EXTENSIONS


def detect_language(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in PY_EXTENSIONS:
        return "python"
    if ext in JS_EXTENSIONS:
        return "javascript"
    return "other"
