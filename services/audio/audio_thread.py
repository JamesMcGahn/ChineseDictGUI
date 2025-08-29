from PySide6.QtCore import QThread, Signal

from .audio_download_worker import AudioDownloadWorker


class AudioThread(QThread):
    updateAnkiAudio = Signal(object)
    start_combine_audio = Signal(str, str, str, int)
    start_whisper = Signal(str, str)

    def __init__(
        self,
        data,
        folder_path=None,
        combine_audio=False,
        combine_audio_export_folder="./",
        combine_audio_export_filename="combined_audio.mp3",
        combine_audio_delay_between_audio=1500,
    ):
        super().__init__()
        self.folder_path = folder_path
        self.data = data
        self.combine_audio = combine_audio
        self.combine_audio_export_folder = combine_audio_export_folder
        self.combine_audio_export_filename = combine_audio_export_filename
        self.combine_audio_delay_between_audio = combine_audio_delay_between_audio
        self.combine_audio_delay_between_audio = combine_audio_delay_between_audio

    def run(self):
        self.worker = AudioDownloadWorker(self.data, self.folder_path)

        self.worker.moveToThread(self)

        self.worker.finished.connect(self.worker_finished)
        self.worker.updateAnkiAudio.connect(self.updateAnkiAudio)
        self.worker.start_whisper.connect(self.start_whisper)
        self.worker.do_work()

    def worker_finished(self):
        self.worker.deleteLater()
        self.wait()
        self.quit()
        if self.combine_audio:
            self.start_combine_audio.emit(
                self.folder_path,
                self.combine_audio_export_filename,
                self.combine_audio_export_folder,
                self.combine_audio_delay_between_audio,
            )
        self.finished.emit()
