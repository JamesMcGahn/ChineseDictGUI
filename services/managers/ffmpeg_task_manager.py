from PySide6.QtCore import Signal, Slot

from base import QObjectBase, ThreadQueueManager
from models.services import CombineAudioPayload, JobRef
from services.audio import CombineAudioThread, WhisperThread


# TODO update whisper to job structure
class FFmpegTaskManager(QObjectBase):
    appshutdown = Signal()
    task_complete = Signal(object, object)

    def __init__(self):
        super().__init__()

        self.queue_manager = ThreadQueueManager("Combine-Whisper")

    @Slot(str, str, str, int, str)
    def combine_audio(self, job_ref: JobRef, payload: CombineAudioPayload):

        combine_audio_thread = CombineAudioThread(job_ref, payload)

        combine_audio_thread.send_logs.connect(self.logging)
        combine_audio_thread.task_complete.connect(self.task_complete)
        self.queue_manager.add_thread(combine_audio_thread)

    def whisper_audio(self, folder, filename):
        whisper_thread = WhisperThread(folder, filename)
        self.appshutdown.connect(whisper_thread.stop)
        whisper_thread.send_logs.connect(self.logging)
        self.queue_manager.add_thread(whisper_thread)
