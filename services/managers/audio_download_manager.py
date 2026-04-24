import time

from PySide6.QtCore import Signal, Slot

from base import QObjectBase, ThreadQueueManager
from db import DatabaseQueryThread
from models.services import JobRequest
from services.audio import AudioThread
from services.sentences.models import Sentence
from services.words.models import Word

from ..audio.models import AudioDownloadPayload

# TODO update db code when context db thread is built out


class AudioDownloadManager(QObjectBase):
    appshutdown = Signal()
    task_complete = Signal(object)

    def __init__(self):
        super().__init__()
        self.queue_manager = ThreadQueueManager("Audio Download")

    @Slot(list)
    def download_audio(self, job: JobRequest[AudioDownloadPayload]):
        audio_thread = AudioThread(job=job)
        audio_thread.task_complete.connect(self.task_complete)
        self.queue_manager.add_thread(audio_thread)

    # TODO Remove Once DB Manager is implemented
    @Slot(object)
    def update_anki_audio(self, obj):
        obj.local_update = int(time.time())

        if isinstance(obj, Sentence):
            self.upwThread = DatabaseQueryThread(
                "sents", "update_sentence", id=obj.id, updates=vars(obj)
            )
            self.upwThread.start()
            self.upwThread.finished.connect(self.upwThread.deleteLater)

        elif isinstance(obj, Word):
            self.upsThread = DatabaseQueryThread(
                "words", "update_word", id=obj.id, updates=vars(obj)
            )
            self.upsThread.start()
            self.upsThread.finished.connect(self.upsThread.deleteLater)
