from PySide6.QtCore import Signal, Slot

from base import QObjectBase, ThreadQueueManager
from models.services import CombineAudioPayload, JobRequest
from services.audio import CombineAudioThread, WhisperThread

from ..audio.models import WhisperPayload


class FFmpegTaskManager(QObjectBase):
    appshutdown = Signal()
    task_complete = Signal(object)

    def __init__(self):
        super().__init__()

        self.queue_manager = ThreadQueueManager("Combine-Whisper")

    @Slot(object, object)
    def combine_audio(self, job: JobRequest[CombineAudioPayload]):

        combine_audio_thread = CombineAudioThread(job)

        combine_audio_thread.send_logs.connect(self.logging)
        combine_audio_thread.task_complete.connect(self.task_complete)
        self.queue_manager.add_thread(combine_audio_thread)

    @Slot(object, object)
    def whisper_audio(self, job: JobRequest[WhisperPayload]):
        whisper_thread = WhisperThread(job)
        self.appshutdown.connect(whisper_thread.stop)
        whisper_thread.send_logs.connect(self.logging)
        whisper_thread.task_complete.connect(self.task_complete)
        self.queue_manager.add_thread(whisper_thread)
