from pathlib import Path
from core.engine import ScanEngine
from core.config import ScanOptions


def test_scan_python_sample():
    engine = ScanEngine()
    sample_dir = Path("samples/python_vuln").resolve()
    result = engine.scan_project(str(sample_dir), ScanOptions())
    assert len(result.findings) >= 6


def test_scan_js_sample():
    engine = ScanEngine()
    sample_dir = Path("samples/js_vuln").resolve()
    result = engine.scan_project(str(sample_dir), ScanOptions())
    assert len(result.findings) >= 6
