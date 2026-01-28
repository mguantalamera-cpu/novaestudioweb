from pathlib import Path
from core.engine import ScanEngine
from core.config import ScanOptions


def test_report_generation(tmp_path):
    engine = ScanEngine()
    sample_dir = Path("samples/python_vuln").resolve()
    result = engine.scan_project(str(sample_dir), ScanOptions())
    patch = engine.generate_patch(result, ScanOptions())
    report = engine.export_report(str(sample_dir), result, patch, None)
    assert Path(report.markdown_path).exists()
    assert Path(report.json_path).exists()
