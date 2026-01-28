from dataclasses import dataclass

DEFAULT_EXCLUDES = {
    ".git",
    ".hg",
    ".svn",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    "dist",
    "build",
    ".pytest_cache",
    ".mypy_cache",
    "reports",
}

MAX_FILE_SIZE_BYTES = 5_000_000

PY_EXTENSIONS = {".py"}
JS_EXTENSIONS = {".js", ".jsx", ".ts", ".tsx"}
TEXT_EXTENSIONS = PY_EXTENSIONS | JS_EXTENSIONS | {".json", ".html", ".yaml", ".yml"}


@dataclass
class ScanOptions:
    strict: bool = False
    no_auto_fix: bool = False
    no_touch_business_logic: bool = True
    use_external_tools: bool = True
