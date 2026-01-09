import time

from PySide6.QtCore import QThread, Signal, Slot

from base import QObjectBase
from db import DatabaseManager, DatabaseQueryThread
from models.dictionary import Lesson, Sentence, Word
from models.services import AudioDownloadPayload, JobRef
from services.audio import AudioThread, CombineAudioThread, WhisperThread


# TODO update db code when context db thread is built out
# TODO untangle whisper and combine logic from workers -> move to lesson manager
class AudioAndWhisperManager(QObjectBase):
    appshutdown = Signal()
    task_complete = Signal(object, object)

    def __init__(self):
        super().__init__()
        self.audio_threads = []
        self.combine_audio_n_whisper_threads = []  # ffmpeg threads

    @Slot(list)
    def download_audio(self, jobref: JobRef, payload: AudioDownloadPayload):
        # TODO get audio folder path from settings

        audio_thread = AudioThread(job_ref=jobref, payload=payload)
        if payload.update_db:
            audio_thread.updateAnkiAudio.connect(self.update_anki_audio)

        audio_thread.start_combine_audio.connect(self.combine_audio)
        audio_thread.done.connect(lambda: self.remove_threads(audio_thread, "Audio"))
        audio_thread.task_complete.connect(self.task_complete)
        audio_thread.start_whisper.connect(self.whisper_audio)
        self.audio_threads.append(audio_thread)
        if len(self.audio_threads) == 1:
            audio_thread.start()

    @Slot(str, str, str, int, str)
    def combine_audio(
        self,
        folder_path,
        output_file_name,
        output_file_folder,
        delay_between_audio,
        project_name,
    ):

        combine_audio_thread = CombineAudioThread(
            folder_path,
            output_file_name,
            output_file_folder,
            delay_between_audio,
            project_name,
        )

        self.combine_audio_n_whisper_threads.append(combine_audio_thread)
        combine_audio_thread.finished.connect(
            lambda: self.remove_threads(combine_audio_thread, "Combine Audio")
        )
        combine_audio_thread.send_logs.connect(self.logging)
        if len(self.combine_audio_n_whisper_threads) == 1:
            combine_audio_thread.start()

    def whisper_audio(self, folder, filename):
        whisper_thread = WhisperThread(folder, filename)
        self.appshutdown.connect(whisper_thread.stop)
        self.combine_audio_n_whisper_threads.append(whisper_thread)
        whisper_thread.done.connect(
            lambda: self.remove_threads(whisper_thread, "Whisper")
        )
        whisper_thread.send_logs.connect(self.logging)
        if len(self.combine_audio_n_whisper_threads) == 1:
            whisper_thread.start()

    def remove_threads(self, thread, thread_type):
        combine_whisper = thread in self.combine_audio_n_whisper_threads
        audio_thread = thread in self.audio_threads

        self.logging(f"Removing {thread_type} thread {thread} from thread queue")
        if combine_whisper:
            self.combine_audio_n_whisper_threads.remove(thread)
        elif audio_thread:
            self.audio_threads.remove(thread)

        try:
            thread.quit()
            thread.wait()
        except Exception:
            self.logging(f"Failed to quit {thread_type} thread {thread}")
        thread.deleteLater()

        if combine_whisper:
            self.maybe_start_next_combo()
        elif audio_thread and self.audio_threads:
            self.audio_threads[0].start()

    def maybe_start_next_combo(self):
        if self.combine_audio_n_whisper_threads:
            head = self.combine_audio_n_whisper_threads[0]
            if not head.isRunning() and not head.isFinished():
                head.start()

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
