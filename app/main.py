import sys
from PySide6 import QtCore, QtWidgets

from core.engine import ScanEngine
from core.config import ScanOptions
from app.worker import Worker


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SecurePatch Desktop")
        self.resize(1100, 720)

        self.engine = ScanEngine()
        self.scan_result = None
        self.patch_plan = None
        self.patch_result = None

        central = QtWidgets.QWidget()
        self.setCentralWidget(central)

        self.path_input = QtWidgets.QLineEdit()
        self.browse_btn = QtWidgets.QPushButton("Browse")
        self.lang_label = QtWidgets.QLabel("Languages: -")

        self.strict_check = QtWidgets.QCheckBox("Strict mode")
        self.no_auto_fix_check = QtWidgets.QCheckBox("Recommendations only (no auto-fix)")
        self.no_touch_logic_check = QtWidgets.QCheckBox("Do not touch business logic")
        self.no_touch_logic_check.setChecked(True)
        self.use_tools_check = QtWidgets.QCheckBox("Use local tools if available")
        self.use_tools_check.setChecked(True)
        self.backup_check = QtWidgets.QCheckBox("Create backup before apply")
        self.backup_check.setChecked(True)

        self.analyze_btn = QtWidgets.QPushButton("Analyze")
        self.patch_btn = QtWidgets.QPushButton("Generate patch")
        self.apply_btn = QtWidgets.QPushButton("Apply patch")
        self.export_btn = QtWidgets.QPushButton("Export report")

        self.results_table = QtWidgets.QTableWidget(0, 6)
        self.results_table.setHorizontalHeaderLabels(
            ["Severity", "Rule", "File", "Line", "Message", "Fixable"]
        )
        self.results_table.horizontalHeader().setStretchLastSection(True)
        self.results_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.results_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        self.diff_view = QtWidgets.QPlainTextEdit()
        self.diff_view.setReadOnly(True)

        self.status_label = QtWidgets.QLabel("Ready")

        top_row = QtWidgets.QHBoxLayout()
        top_row.addWidget(QtWidgets.QLabel("Project"))
        top_row.addWidget(self.path_input)
        top_row.addWidget(self.browse_btn)

        options_row = QtWidgets.QHBoxLayout()
        options_row.addWidget(self.strict_check)
        options_row.addWidget(self.no_auto_fix_check)
        options_row.addWidget(self.no_touch_logic_check)
        options_row.addWidget(self.use_tools_check)
        options_row.addWidget(self.backup_check)
        options_row.addStretch(1)

        actions_row = QtWidgets.QHBoxLayout()
        actions_row.addWidget(self.analyze_btn)
        actions_row.addWidget(self.patch_btn)
        actions_row.addWidget(self.apply_btn)
        actions_row.addWidget(self.export_btn)
        actions_row.addStretch(1)

        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        splitter.addWidget(self.results_table)
        splitter.addWidget(self.diff_view)
        splitter.setSizes([500, 600])

        layout = QtWidgets.QVBoxLayout(central)
        layout.addLayout(top_row)
        layout.addWidget(self.lang_label)
        layout.addLayout(options_row)
        layout.addLayout(actions_row)
        layout.addWidget(splitter)
        layout.addWidget(self.status_label)

        self.thread_pool = QtCore.QThreadPool.globalInstance()

        self.browse_btn.clicked.connect(self.on_browse)
        self.analyze_btn.clicked.connect(self.on_analyze)
        self.patch_btn.clicked.connect(self.on_generate_patch)
        self.apply_btn.clicked.connect(self.on_apply_patch)
        self.export_btn.clicked.connect(self.on_export_report)

    def on_browse(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select project")
        if path:
            self.path_input.setText(path)

    def _options(self):
        return ScanOptions(
            strict=self.strict_check.isChecked(),
            no_auto_fix=self.no_auto_fix_check.isChecked(),
            no_touch_business_logic=self.no_touch_logic_check.isChecked(),
            use_external_tools=self.use_tools_check.isChecked(),
        )

    def on_analyze(self):
        project = self.path_input.text().strip()
        if not project:
            self.status_label.setText("Select a project folder")
            return
        self.status_label.setText("Scanning...")
        worker = Worker(self.engine.scan_project, project, self._options())
        worker.signals.finished.connect(self.on_scan_finished)
        worker.signals.error.connect(self.on_worker_error)
        self.thread_pool.start(worker)

    def on_scan_finished(self, result):
        self.scan_result = result
        self.patch_plan = None
        self.patch_result = None
        self.diff_view.setPlainText("")
        self.results_table.setRowCount(0)
        for finding in result.findings:
            row = self.results_table.rowCount()
            self.results_table.insertRow(row)
            self.results_table.setItem(row, 0, QtWidgets.QTableWidgetItem(finding.severity.value))
            self.results_table.setItem(row, 1, QtWidgets.QTableWidgetItem(finding.rule_id))
            self.results_table.setItem(row, 2, QtWidgets.QTableWidgetItem(finding.file_path))
            self.results_table.setItem(row, 3, QtWidgets.QTableWidgetItem(str(finding.line)))
            self.results_table.setItem(row, 4, QtWidgets.QTableWidgetItem(finding.message))
            self.results_table.setItem(row, 5, QtWidgets.QTableWidgetItem("yes" if finding.fixable else "no"))
        langs = ", ".join(sorted(result.language_stats.keys())) or "-"
        self.lang_label.setText(f"Languages: {langs}")
        self.status_label.setText(f"Findings: {len(result.findings)}")

    def on_generate_patch(self):
        if not self.scan_result:
            self.status_label.setText("Run analysis first")
            return
        self.status_label.setText("Generating patch...")
        worker = Worker(self.engine.generate_patch, self.scan_result, self._options())
        worker.signals.finished.connect(self.on_patch_generated)
        worker.signals.error.connect(self.on_worker_error)
        self.thread_pool.start(worker)

    def on_patch_generated(self, plan):
        self.patch_plan = plan
        self.diff_view.setPlainText(plan.diff)
        self.status_label.setText(f"Patch ready. Files: {len(plan.file_changes)}")

    def on_apply_patch(self):
        if not self.patch_plan:
            self.status_label.setText("Generate patch first")
            return
        self.status_label.setText("Applying patch...")
        worker = Worker(self.engine.apply_patch, self.patch_plan, self.backup_check.isChecked())
        worker.signals.finished.connect(self.on_patch_applied)
        worker.signals.error.connect(self.on_worker_error)
        self.thread_pool.start(worker)

    def on_patch_applied(self, result):
        self.patch_result = result
        if result.errors:
            self.status_label.setText("Apply finished with errors")
        else:
            self.status_label.setText("Patch applied")

    def on_export_report(self):
        if not self.scan_result:
            self.status_label.setText("Run analysis first")
            return
        project = self.path_input.text().strip()
        if not project:
            self.status_label.setText("Select a project folder")
            return
        self.status_label.setText("Exporting report...")
        worker = Worker(self.engine.export_report, project, self.scan_result, self.patch_plan, self.patch_result)
        worker.signals.finished.connect(self.on_report_exported)
        worker.signals.error.connect(self.on_worker_error)
        self.thread_pool.start(worker)

    def on_report_exported(self, report_paths):
        self.status_label.setText(f"Report saved in {report_paths.output_dir}")

    def on_worker_error(self, trace):
        self.status_label.setText("Error - check console")
        print(trace)


def main():
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
