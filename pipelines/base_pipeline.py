from PySide6.QtCore import Signal

from base import QObjectBase
from models.services import JobRef


class BaseLessonPipeline(QObjectBase):
    send_sents_sig = Signal(list, bool)
    send_words_sig = Signal(list, bool)
    pipeline_finished = Signal(str)

    def process(self, input_data):
        raise NotImplementedError

    def on_task_completed(self, job: JobRef, payload):
        raise NotImplementedError
