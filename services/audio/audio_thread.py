from PySide6.QtCore import QThread, Signal

from .audio_download_worker import AudioDownloadWorker


class AudioThread(QThread):
    updateAnkiAudio = Signal(object)

    def __init__(self, data, folder_path=None):
        super().__init__()
        self.folder_path = folder_path
        self.data = data

    def run(self):
        self.worker = AudioDownloadWorker(self.data, self.folder_path)

        self.worker.moveToThread(self)

        self.worker.finished.connect(self.worker_finished)
        self.worker.updateAnkiAudio.connect(self.updateAnkiAudio)
        self.worker.do_work()

    def worker_finished(self):
        self.worker.deleteLater()
        self.wait()
        self.quit()
        self.finished.emit()
