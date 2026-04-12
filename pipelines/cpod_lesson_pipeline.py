from typing import Any

from PySide6.QtCore import QTimer, Signal

from base import ThreadQueueManager
from base.enums import (
    DBJOBTYPE,
    DBOPERATION,
    EXTRACTDATASOURCE,
    FAILURESTRATEGY,
    JOBSTATUS,
    LESSONLEVEL,
    LESSONSTATUS,
    LESSONTASK,
    PIPELINEJOBTYPE,
    WHISPERPROVIDER,
)
from models.dictionary import Lesson
from models.pipelines import (
    EmitUIEventAction,
    FileWriteAction,
    LessonPipelinePayload,
    PipelineAction,
    PipelineServiceContainer,
    TaskDefinition,
    TaskRuntimeState,
)
from models.services import (
    AudioDownloadPayload,
    CombineAudioPayload,
    CPodLessonPayload,
    JobRef,
    JobRequest,
    JobResponse,
    LingqLessonPayload,
    WhisperPayload,
)
from models.services.database import DBJobPayload
from models.services.database.write import InsertOnePayload
from services.processors import LessonFileService
from services.processors.cpod.cpod_processor_registry import CpodProcessorRegistry

# TODO - global registry for processors and transformers
from services.transformers.cpod.cpod_transformer_registry import CpodTransformerRegistry
from services.transformers.cpod.utils.lesson_helpers import extract_slug
from utils.files import PathManager

from .base_pipeline import BaseLessonPipeline
from .cpod_task_config import TASK_GRAPH

# TODO ADD STEP ERROR HANDLING


class CPodLessonPipeline(BaseLessonPipeline):
    scraping_active = Signal(bool)

    # TODO SERVICE CONTAINER?
    def __init__(
        self, spec: LessonPipelinePayload, service_cont: PipelineServiceContainer
    ):
        super().__init__()
        self.spec = spec
        self.ffmpeg_task_manager = service_cont.ffmpeg
        self.audio_download_manager = service_cont.audio
        self.lingq_workflow_manager = service_cont.lingq
        self.db = service_cont.db
        self.session_registry = service_cont.session
        self.cpod_lesson_manager = service_cont.cpod_lesson

        self.transformer = CpodTransformerRegistry().get_transformer(
            PIPELINEJOBTYPE.LESSONS
        )

        self.thread_queue_manager = ThreadQueueManager("Lesson")
        self.base_path = "./test/"

        self.expected_tasks = set()
        self.completed_tasks = set()
        self.queue_id = None
        self.lesson = None
        self.processor = CpodProcessorRegistry().get_processor(PIPELINEJOBTYPE.LESSONS)
        self.writer = LessonFileService()

        self.ffmpeg_task_manager.task_complete.connect(self.on_task_completed)
        self.audio_download_manager.task_complete.connect(self.on_task_completed)
        self.db.task_complete.connect(self.on_task_completed)
        self.lingq_workflow_manager.task_complete.connect(self.on_task_completed)
        self.cpod_lesson_manager.task_complete.connect(self.on_task_completed)

        # TODO get from settings
        self.collections = {
            LESSONLEVEL.NEWBIE: {
                "lesson": "2310680",
                "sents": "2547067",
                "dialogue": "2547067",
            },
            LESSONLEVEL.ELEMENTARY: {
                "lesson": "2653032",
                "sents": "2653032",
                "dialogue": "2653032",
            },
            LESSONLEVEL.PRE_INTERMEDIATE: {
                "lesson": "2653032",
                "sents": "2653032",
                "dialogue": "2653032 ",
            },
            LESSONLEVEL.INTERMEDIATE: {
                "lesson": "2491860",
                "sents": "2402549",
                "dialogue": "2402549",
            },
            LESSONLEVEL.ADVANCED: {
                "lesson": "2310680",
                "sents": "2310680",
                "dialogue": "2310680",
            },
            LESSONLEVEL.MEDIA: {
                "lesson": "2310680",
                "sents": "2310680",
                "dialogue": "2310680",
            },
        }

        self.dispatchers = {
            LESSONTASK.LESSON_AUDIO: self.dispatch_lesson_audio,
            LESSONTASK.COMBINE_AUDIO: self.dispatch_combine_audio,
            LESSONTASK.SAVE_LESSON: self.dispatch_save_lesson,
            LESSONTASK.AUDIO: self.dispatch_lesson_parts_audio,
            LESSONTASK.LINGQ_LESSON: self.dispatch_lingq_lesson,
            LESSONTASK.TRANSCRIBE: self.dispatch_transcribe_lesson,
            LESSONTASK.LINGQ_SENTS: self.dispatch_lingq_sents,
            LESSONTASK.LINGQ_DIALOGUE: self.dispatch_lingq_dialogue,
            LESSONTASK.INFO: self.dispatch_cpod_lesson_part,
            LESSONTASK.DIALOGUE: self.dispatch_cpod_lesson_part,
            LESSONTASK.EXPANSION: self.dispatch_cpod_lesson_part,
            LESSONTASK.GRAMMAR: self.dispatch_cpod_lesson_part,
            LESSONTASK.VOCAB: self.dispatch_cpod_lesson_part,
            LESSONTASK.CHECK: self.dispatch_cpod_lesson_part,
        }

        self.action_map = {
            FileWriteAction: self.writer.write_file,
            EmitUIEventAction: self.handle_ui_event_action,
        }

        self.TASK_STATE: dict[LESSONTASK, TaskRuntimeState] = {}

    def process(self):

        self.queue_id = self.spec.queue_id

        slug = extract_slug(self.spec.url)
        self.lesson = Lesson(
            provider=self.spec.provider,
            url=self.spec.url,
            check_dup_sents=self.spec.check_dup_sents,
            transcribe_lesson=self.spec.transcribe_lesson,
            queue_id=self.queue_id,
            slug=slug,
        )
        self.build_expected_tasks(self.spec)

        job = JobRequest(
            id=self.queue_id,
            task=LESSONTASK.INFO,
            payload=CPodLessonPayload(url=self.spec.url, slug=slug),
        )

        self.cpod_lesson_manager.get_lesson_part(job, EXTRACTDATASOURCE.SCRAPE)
        # session = self.session_registry.for_provider(PROVIDERS.CPOD)
        # lesson_thread = LessonScraperThread([job], session=session)
        # lesson_thread.task_complete.connect(self.on_task_completed)

        # lesson_thread.finished.connect(
        #     lambda: self.thread_queue_manager.on_finished_thread(lesson_thread)
        # )
        # self.thread_queue_manager.add_thread(lesson_thread)

    def job_to_lesson_status(self, job_status: JOBSTATUS):
        try:
            return LESSONSTATUS[job_status.name]
        except KeyError as e:
            if job_status == JOBSTATUS.PARTIAL_ERROR:
                return LESSONSTATUS.ERROR
            else:
                raise ValueError(f"Unsupported Job Status: {job_status}") from e

    def build_expected_tasks(self, spec: LessonPipelinePayload):
        core_tasks = {
            LESSONTASK.INFO,
            LESSONTASK.DIALOGUE,
            LESSONTASK.LESSON_AUDIO,
            LESSONTASK.CHECK,
            LESSONTASK.SAVE_LESSON,
            LESSONTASK.AUDIO,
            LESSONTASK.COMBINE_AUDIO,
        }
        self.expected_tasks.update(core_tasks)
        if spec.create_lingq_lessons:
            core_linq_tasks = {
                LESSONTASK.LINGQ_DIALOGUE,
                LESSONTASK.LINGQ_SENTS,
            }
            self.expected_tasks.update(core_linq_tasks)
        if spec.transcribe_lesson:
            self.expected_tasks.add(LESSONTASK.TRANSCRIBE)
            if spec.create_lingq_lessons:
                self.expected_tasks.add(LESSONTASK.LINGQ_LESSON)

    def get_next_tasks(self, task):
        task_def = self._get_task_def(task)
        return task_def.next_tasks

    def dispatch(self, task: LESSONTASK, lesson: Lesson):
        dispatcher = self.dispatchers.get(task, None)
        if dispatcher is None:
            raise ValueError(f"No dispatcher defined for task: {task}")

        dispatcher(task=task, lesson=lesson)

    def on_task_completed(self, job: JobResponse[Any]):
        if job.job_ref.id != self.queue_id or self.lesson is None:
            return
        self.logging(
            f"Received response for Task: {job.job_ref.task} - Status: {job.job_ref.status}"
        )
        self.update_lesson_status(
            job.job_ref.task, self.job_to_lesson_status(job.job_ref.status)
        )

        if job.job_ref.status == JOBSTATUS.COMPLETE:
            task_def = self._get_task_def(job.job_ref.task)
            capability = task_def.capability
            if capability and capability.transform:
                payload = self.transformer.process(
                    job.job_ref.task, self.lesson, job.payload
                )
                if payload.success:
                    self.handle_success(job.job_ref, payload, self.lesson)
                else:
                    self.handle_failure(job.job_ref, payload, self.lesson)
            else:
                self.handle_success(job.job_ref, job.payload, self.lesson)

            next_tasks = self.get_next_tasks(job.job_ref.task)
            for task in next_tasks:
                self.dispatch(task, self.lesson)

        elif job.job_ref.status == JOBSTATUS.ERROR:
            self.handle_failure(job.job_ref, job.payload, self.lesson)
        else:
            return
        # FEATURE : allow for threshold of number of errors, setting

    def handle_success(self, job: JobRef, payload, lesson: Lesson):
        self.update_completed_tasks(job.task)
        task_def = self._get_task_def(job.task)
        capability = task_def.capability

        state = self._get_task_state(job.task)
        state.retry_attempts = 0
        state.source_index = 0
        if capability and capability.process:
            processor_response = self.processor.apply(
                task=job.task, lesson=self.lesson, payload=payload
            )
            self.execute_actions(actions=processor_response.actions)

    def execute_actions(self, actions: list[PipelineAction]):
        for action in actions:
            self.execute_action(action=action)

    def execute_action(self, action: PipelineAction):
        for action_type, handler in self.action_map.items():
            if isinstance(action, action_type):
                return handler(action)
        self.logging(
            f"{self.__class__.__name__}: {type(action)} has not been implemented as an action."
        )
        raise NotImplementedError

    def handle_ui_event_action(self, action: EmitUIEventAction):
        self.ui_event.emit(action.event)

    def update_completed_tasks(self, task: LESSONTASK):
        self.completed_tasks.add(task)
        self.check_pipeline_completed()
        print("COMPLETED TASKS", self.completed_tasks)

    def handle_failure(self, job: JobRef, payload, lesson: Lesson):
        task_def = self._get_task_def(job.task)
        policy = task_def.policy
        self.logging(f"{job.task} failed for {lesson.title}", "ERROR")
        state = self._get_task_state(job.task)
        attempts = state.retry_attempts

        if policy.failure_strategy == FAILURESTRATEGY.IGNORE:
            self.update_completed_tasks(job.task)
            next_tasks = self.get_next_tasks(job.task)
            for task in next_tasks:
                self.dispatch(task, self.lesson)
            return

        if policy.failure_strategy == FAILURESTRATEGY.FALLBACK:
            sources = task_def.sources or []
            if state.source_index < len(sources) - 1:
                state.source_index += 1
                self.dispatch(job.task, lesson)
                return
        if policy.failure_strategy == FAILURESTRATEGY.RETRY:
            if attempts < policy.max_retries:
                state.retry_attempts += 1
                attempts = state.retry_attempts
                if policy.backoff:
                    delay = policy.retry_delay_ms * (2**attempts)
                else:
                    delay = policy.retry_delay_ms

                self.logging(
                    f"Retrying {job.task} for {lesson.title} - Attempt: {attempts}/{policy.max_retries}"
                )
                QTimer.singleShot(delay, lambda: self.dispatch(job.task, lesson))
                return
        self.logging(f"{job.task} failed completely", "ERROR")
        if policy.is_criticial:
            # TODO complete failure
            pass
        return

    def update_lesson_status(
        self, lesson_task: LESSONTASK, lesson_status: LESSONSTATUS
    ):
        self.lesson.task = lesson_task
        self.lesson.status = lesson_status

    ## DISPATCH HANDLERS

    def _get_task_def(self, task: LESSONTASK) -> TaskDefinition:
        return TASK_GRAPH.get(task, TaskDefinition())

    def _get_task_state(self, task: LESSONTASK) -> TaskRuntimeState:
        return self.TASK_STATE.setdefault(task, TaskRuntimeState())

    def _get_current_source(self, task: LESSONTASK):
        state = self._get_task_state(task)
        task_def = self._get_task_def(task)
        sources = task_def.sources

        if state.source_index >= len(sources):
            raise RuntimeError(f"Invalid source index for {task}")
        return sources[state.source_index]

    def dispatch_cpod_lesson_part(self, task: LESSONTASK, lesson: Lesson):
        source = self._get_current_source(task)
        job = JobRequest(
            id=self.queue_id,
            task=task,
            payload=CPodLessonPayload(
                url=lesson.url,
                slug=lesson.slug,
                lesson_id=lesson.lesson_id,
            ),
        )
        self.cpod_lesson_manager.get_lesson_part(job, source)

    def dispatch_transcribe_lesson(self, task: LESSONTASK, lesson: Lesson):
        # TODO WHISPER SETTINGS From Settings
        if lesson.transcribe_lesson:
            self.ffmpeg_task_manager.whisper_audio(
                JobRequest(
                    id=lesson.queue_id,
                    task=task,
                    payload=WhisperPayload(
                        provider=WHISPERPROVIDER.WHISPER,
                        file_filename="lesson.mp3",
                        file_folder_path=lesson.storage_path,
                        model_name="tiny",
                    ),
                )
            )

    def dispatch_lesson_audio(self, task: LESSONTASK, lesson: Lesson):
        self.audio_download_manager.download_audio(
            job=JobRequest(
                id=lesson.queue_id,
                task=task,
                payload=AudioDownloadPayload(
                    audio_urls=lesson.lesson_parts.lesson_audios,
                    export_path=lesson.storage_path,
                    project_name=lesson.title,
                ),
            )
        )

    def dispatch_combine_audio(self, task: LESSONTASK, lesson: Lesson):
        self.ffmpeg_task_manager.combine_audio(
            JobRequest(
                id=lesson.queue_id,
                task=task,
                payload=CombineAudioPayload(
                    combine_folder_path=f"{lesson.storage_path}audio",
                    export_file_name="sentences.mp3",
                    export_path=lesson.storage_path,
                    delay_between_audio=1500,
                    project_name=lesson.title,
                ),
            )
        )

    def dispatch_save_lesson(self, task: LESSONTASK, lesson: Lesson):
        self.db.write(
            JobRequest(
                id=lesson.queue_id,
                task=task,
                payload=DBJobPayload(
                    kind=DBJOBTYPE.LESSONS,
                    operation=DBOPERATION.INSERT_ONE,
                    data=InsertOnePayload(data=lesson),
                ),
            )
        )

    def dispatch_lesson_parts_audio(self, task: LESSONTASK, lesson: Lesson):
        all_sents = lesson.lesson_parts.all_sentences
        words = lesson.lesson_parts.vocab

        sents_words_with_in_order = []
        for i, sent_item in enumerate(all_sents + words):
            sent_item.id = i + 1
            sents_words_with_in_order.append(sent_item)

        if sents_words_with_in_order:
            self.logging(
                f"Adding - {lesson.title} - Sentences & Words Audio to Download Queue."
            )

            self.audio_download_manager.download_audio(
                JobRequest(
                    id=lesson.queue_id,
                    task=task,
                    payload=AudioDownloadPayload(
                        audio_urls=sents_words_with_in_order,
                        export_path=f"{lesson.storage_path}audio",
                        project_name=lesson.title,
                    ),
                )
            )

    def dispatch_lingq_lesson(self, task: LESSONTASK, lesson: Lesson):
        if not lesson.transcribe_lesson:
            return
        lesson_txt = f"{lesson.storage_path}lesson.txt"
        lesson_audio = f"{lesson.storage_path}lesson.mp3"

        lesson_txt_exists = PathManager.path_exists(
            path=lesson_txt,
            makepath=False,
        )
        lesson_audio_exists = PathManager.path_exists(
            path=lesson_audio,
            makepath=False,
        )
        if not lesson_txt_exists and lesson_audio_exists:
            # TODO raise error
            return
        collection = self.collections.get(
            lesson.level,
            {"lesson": "2310680", "sents": "2310680", "dialogue": "2310680"},
        )

        job_list = []

        lesson = JobRequest[LingqLessonPayload](
            id=lesson.queue_id,
            task=task,
            payload=LingqLessonPayload(
                title=f"{lesson.title} - Lesson",
                collection=collection["lesson"],
                audio_file_name="lesson.mp3",
                audio_file_path=lesson_audio,
                text_file_name="lesson.txt",
                text_file_path=lesson_txt,
                project_name=lesson.title,
            ),
        )

        job_list.append(lesson)
        self.lingq_workflow_manager.create_lingq_lesson(jobs=job_list)

    def dispatch_lingq_sents(self, task: LESSONTASK, lesson: Lesson):
        sents_text = f"{lesson.storage_path}sentences.txt"
        sents_audio = f"{lesson.storage_path}sentences.mp3"

        sents_audio_exists = PathManager.path_exists(
            path=sents_audio,
            makepath=False,
        )

        sents_txt_exists = PathManager.path_exists(
            path=sents_text,
            makepath=False,
        )

        collection = self.collections.get(
            lesson.level,
            {"lesson": "2310680", "sents": "2310680", "dialogue": "2310680"},
        )

        if sents_audio_exists and sents_txt_exists:
            lingq_sent = JobRequest[LingqLessonPayload](
                id=lesson.queue_id,
                task=task,
                payload=LingqLessonPayload(
                    title=f"{lesson.title} - Sents",
                    collection=collection["sents"],
                    audio_file_name="sentences.mp3",
                    audio_file_path=sents_audio,
                    text_file_name="sentences.txt",
                    text_file_path=sents_text,
                    project_name=lesson.title,
                ),
            )

            self.lingq_workflow_manager.create_lingq_lesson(jobs=[lingq_sent])

    def dispatch_lingq_dialogue(self, task: LESSONTASK, lesson: Lesson):

        dialogue_text = f"{lesson.storage_path}dialogue.txt"
        dialogue_audio = f"{lesson.storage_path}dialogue.mp3"

        dialogue_audio_exists = PathManager.path_exists(
            path=dialogue_audio,
            makepath=False,
        )
        dialogue_txt_exists = PathManager.path_exists(
            path=dialogue_text,
            makepath=False,
        )

        collection = self.collections.get(
            lesson.level,
            {"lesson": "2310680", "sents": "2310680", "dialogue": "2310680"},
        )
        job_list = []

        if dialogue_audio_exists and dialogue_txt_exists:
            dialogue = JobRequest[LingqLessonPayload](
                id=lesson.queue_id,
                task=task,
                payload=LingqLessonPayload(
                    title=f"{lesson.title} - Dialogue",
                    collection=collection["dialogue"],
                    audio_file_name="dialogue.mp3",
                    audio_file_path=dialogue_audio,
                    text_file_name="dialogue.txt",
                    text_file_path=dialogue_text,
                    project_name=lesson.title,
                ),
            )

            job_list.append(dialogue)

        self.lingq_workflow_manager.create_lingq_lesson(jobs=job_list)
        print("Ready for Lingq")

    def check_pipeline_completed(self):

        if self.completed_tasks >= self.expected_tasks:
            self.pipeline_finished.emit(self.queue_id)
        else:
            print("not finished")
            print(self.expected_tasks, self.completed_tasks)
