import hashlib
from pathlib import Path

from core.config import DEFAULT_EXCLUDES, MAX_FILE_SIZE_BYTES


def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()


def is_binary_string(data: bytes) -> bool:
    if not data:
        return False
    text_chars = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)))
    return bool(data.translate(None, text_chars))


def read_text_file(path: Path, max_bytes: int = MAX_FILE_SIZE_BYTES) -> str:
    if path.stat().st_size > max_bytes:
        raise ValueError("File too large")
    data = path.read_bytes()
    if is_binary_string(data):
        raise ValueError("Binary file")
    return data.decode("utf-8", errors="replace")


def safe_walk(root: Path):
    for dirpath, dirnames, filenames in root.walk():
        cleaned = []
        for d in dirnames:
            if d in DEFAULT_EXCLUDES:
                continue
            full = Path(dirpath) / d
            if full.is_symlink():
                continue
            cleaned.append(d)
        dirnames[:] = cleaned
        for name in filenames:
            path = Path(dirpath) / name
            if path.is_symlink():
                continue
            yield path


def relative_path(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)
