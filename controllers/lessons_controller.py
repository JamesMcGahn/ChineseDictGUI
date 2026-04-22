from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from services.managers import DatabaseServiceManager
    from services.managers import LessonPipelineManager
    from services.words.models import Word
    from models.dictionary import Sentence

from uuid import uuid4

from PySide6.QtCore import Signal, Slot

from base import QObjectBase
from base.enums import LOGLEVEL, UIEVENTTYPE
from base.events import SentencesEvent, ToastEvent, UIEvent, WordsEvent
from components.toasts.qtoast.enums import QTOASTSTATUS
from pipelines.enums import PIPELINEJOBTYPE, PIPELINESTATUS
from pipelines.models import (
    LessonPipelinePayload,
    LessonPipelineResponse,
    PipelineRequest,
    PipelineResponse,
)
from services.lessons.enums import LESSONPROVIDERS
from services.lessons.models import LessonWorkFlowRequest


class LessonsController(QObjectBase):
    ui_event = Signal(object)

    def __init__(
        self, db_service: DatabaseServiceManager, lesson_pipeline: LessonPipelineManager
    ):
        super().__init__()
        self.db_service = db_service
        self.lesson_pipeline = lesson_pipeline
        self._active_jobs: dict[str, LessonWorkFlowRequest] = {}

        self.lesson_pipeline.ui_event.connect(self.receive_ui_event)
        self.lesson_pipeline.pipeline_response.connect(self.receive_pipeline_response)

    def add_to_lesson_queue(self, lesson_specs: list[LessonWorkFlowRequest]):
        requests = []
        for spec in lesson_specs:
            queue_id = str(uuid4())

            request = PipelineRequest(
                job_type=PIPELINEJOBTYPE.LESSONS,
                payload=LessonPipelinePayload(
                    queue_id=queue_id,
                    provider=LESSONPROVIDERS.CPOD,
                    url=spec.url,
                    check_dup_sents=spec.check_dup_sents,
                    check_dup_words=spec.check_dup_words,
                    transcribe_lesson=spec.transcribe_lesson,
                    create_lingq_lessons=True,
                ),
            )
            requests.append(request)
            self._active_jobs[queue_id] = request
        self.lesson_pipeline.add_lessons_to_queue(requests)

    @Slot(object)
    def receive_pipeline_response(
        self, response: PipelineResponse[LessonPipelineResponse]
    ):
        job = self._active_jobs.get(response.payload.queue_id, None)
        if job is None:
            return

        self.logging(f"Pipeline Completed - {response.payload.queue_id}")
        send_toast = False
        p = response.payload
        if response.status == PIPELINESTATUS.COMPLETE:
            self._active_jobs.pop(response.payload.queue_id)
            status = QTOASTSTATUS.SUCCESS
            log_level = LOGLEVEL.INFO
            title = "Lesson Import Completed"
            send_toast = True
        elif response.status in (PIPELINESTATUS.ERROR, PIPELINESTATUS.PARTIAL_ERROR):
            self._active_jobs.pop(response.payload.queue_id)
            status = QTOASTSTATUS.ERROR
            log_level = LOGLEVEL.INFO
            title = "Lesson Import Errored"
            send_toast = True

        if send_toast:
            print("sending toast")
            self.ui_event.emit(
                UIEvent(
                    event_type=UIEVENTTYPE.DISPLAY,
                    payload=ToastEvent(
                        message=p.message,
                        title=title,
                        toast_level=status,
                        log_level=log_level,
                    ),
                )
            )

    @Slot(object)
    def receive_ui_event(self, event: UIEvent):
        if isinstance(event.payload, SentencesEvent):
            self.handle_sentence_event(event)
            return
        if isinstance(event.payload, WordsEvent):
            self.handle_word_event(event)
            return

    def handle_sentence_event(self, event: UIEvent[SentencesEvent]):
        if event.payload.check_duplicates:
            sentences = self.check_sentence_duplicates(event.payload.sentences)

            deduped = UIEvent(
                event_type=event.event_type,
                payload=SentencesEvent(sentences=sentences, check_duplicates=True),
            )
            self.ui_event.emit(deduped)
        else:
            self.ui_event.emit(event)
        return

    def check_sentence_duplicates(self, sentences: list[Sentence]):
        result = self.db_service.read.sentences.exists(sentences)
        self.logging(f"Found {len(result)} sentences that already exist in the db.")
        unique_sentences = [
            sentence for sentence in sentences if sentence.chinese not in result
        ]
        return unique_sentences

    def handle_word_event(self, event: UIEvent[WordsEvent]):
        if event.payload.check_duplicates:
            words = self.check_word_duplicates(event.payload.words)
            deduped = UIEvent(
                event_type=event.event_type,
                payload=WordsEvent(words=words, check_duplicates=True),
            )
            self.ui_event.emit(deduped)
        else:
            self.ui_event.emit(event)
        return

    def check_word_duplicates(self, words: list[Word]):
        result = self.db_service.read.words.exists(words)
        self.logging(f"Found {len(result)} words that already exist in the db.")
        unique_words = [word for word in words if word.chinese not in result]
        return unique_words

    @Slot(list)
    def save_words(self, words):
        pass

    @Slot(list)
    def save_sentences(self, sentences):
        pass
