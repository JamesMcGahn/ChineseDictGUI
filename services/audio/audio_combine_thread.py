from PySide6.QtCore import QThread, Signal, Slot

from .audio_combine_worker import AudioCombineWorker


class CombineAudioThread(QThread):
    updateAnkiAudio = Signal(object)
    start_combine_audio = Signal(str)
    stop_worker = Signal()

    def __init__(
        self,
        folder_path: str,
        output_file_name: str,
        output_file_folder: str,
        silence_ms: int = 500,
    ):
        super().__init__()
        self.folder_path = folder_path
        self.output_file_name = output_file_name
        self.output_file_folder = output_file_folder
        self.silence_ms = silence_ms

    def run(self):
        self.worker = AudioCombineWorker(
            self.folder_path,
            self.output_file_name,
            self.output_file_folder,
            self.silence_ms,
        )

        self.worker.moveToThread(self)
        self.worker.finished.connect(self.worker_finished)
        self.stop_worker.connect(self.worker.stop)
        self.worker.do_work()

    def worker_finished(self):
        self.worker.deleteLater()
        self.wait()
        self.quit()

    @Slot()
    def stop(self):
        if self.isRunning():
            self.stop_worker.emit()
