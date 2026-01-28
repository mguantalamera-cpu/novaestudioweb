import traceback
from PySide6 import QtCore


class WorkerSignals(QtCore.QObject):
    finished = QtCore.Signal(object)
    error = QtCore.Signal(str)
    progress = QtCore.Signal(str)


class Worker(QtCore.QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @QtCore.Slot()
    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
            self.signals.finished.emit(result)
        except Exception:
            self.signals.error.emit(traceback.format_exc())
