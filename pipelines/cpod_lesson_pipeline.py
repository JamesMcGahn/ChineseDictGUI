from typing import Any

from PySide6.QtCore import QTimer, Signal

from base import ThreadQueueManager
from base.enums import (
    DBJOBTYPE,
    DBOPERATION,
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
    TaskCapability,
    TaskPolicy,
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

        self.flow_map = {
            LESSONTASK.INFO: [
                LESSONTASK.LESSON_AUDIO,
                LESSONTASK.DIALOGUE,
                LESSONTASK.EXPANSION,
                LESSONTASK.GRAMMAR,
                LESSONTASK.VOCAB,
                LESSONTASK.CHECK,
            ],
            LESSONTASK.CHECK: [LESSONTASK.SAVE_LESSON, LESSONTASK.AUDIO],
            LESSONTASK.AUDIO: [LESSONTASK.COMBINE_AUDIO],
            LESSONTASK.TRANSCRIBE: [LESSONTASK.LINGQ_LESSON],
            LESSONTASK.LESSON_AUDIO: [LESSONTASK.TRANSCRIBE],
            LESSONTASK.COMBINE_AUDIO: [
                LESSONTASK.LINGQ_DIALOGUE,
                LESSONTASK.LINGQ_SENTS,
            ],
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
            LESSONTASK.DIALOGUE: self.dispatch_dialogue,
            LESSONTASK.EXPANSION: self.dispatch_expansion,
            LESSONTASK.GRAMMAR: self.dispatch_grammar,
            LESSONTASK.VOCAB: self.dispatch_vocab,
            LESSONTASK.CHECK: self.dispatch_check,
        }

        self.action_map = {
            FileWriteAction: self.writer.write_file,
            EmitUIEventAction: self.handle_ui_event_action,
        }

        self.TASK_POLICY: dict[LESSONTASK, TaskPolicy] = {
            LESSONTASK.LINGQ_SENTS: TaskPolicy(max_retries=2, retry_delay_ms=5_000),
            LESSONTASK.LINGQ_DIALOGUE: TaskPolicy(max_retries=2, retry_delay_ms=5_000),
        }

        self.TASK_CAPABILITIES: dict[LESSONTASK, TaskCapability] = {
            LESSONTASK.INFO: TaskCapability(transform=True, process=True),
            LESSONTASK.DIALOGUE: TaskCapability(transform=True, process=True),
            LESSONTASK.EXPANSION: TaskCapability(transform=True, process=True),
            LESSONTASK.GRAMMAR: TaskCapability(transform=True, process=True),
            LESSONTASK.VOCAB: TaskCapability(transform=True, process=True),
            LESSONTASK.CHECK: TaskCapability(transform=False, process=True),
        }

        self.task_retry_attempts = {}

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

        self.cpod_lesson_manager.get_lesson_part(job)
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
        return self.flow_map.get(task, [])

    def dispatch(self, task: LESSONTASK, lesson: Lesson):
        dispatcher = self.dispatchers.get(task, None)

        if dispatcher is None:
            raise ValueError(f"No dispatcher defined for task: {task}")

        dispatcher(lesson=lesson)

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

            capability = self.TASK_CAPABILITIES.get(job.job_ref.task)
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

        capability = self.TASK_CAPABILITIES.get(job.task)
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
        policy = self.TASK_POLICY.get(job.task, TaskPolicy())
        self.logging(f"{job.task} failed for {lesson.title}", "ERROR")

        attempts = self.task_retry_attempts.get(job.task, 0)

        if policy.max_retries == 0:
            self.logging(f"No Retry Policy for {job.task} - {lesson.title}", "DEBUG")
            return

        if attempts < policy.max_retries:
            attempts += 1
            self.logging(
                f"Retrying {job.task} for {lesson.title} - Attempt: {attempts}/{policy.max_retries}",
                "INFO",
            )
            if policy.backoff:
                delay = policy.retry_delay_ms * (2**attempts)
            else:
                delay = policy.retry_delay_ms
            self.task_retry_attempts[job.task] = attempts
            QTimer.singleShot(delay, lambda: self.dispatch(job.task, self.lesson))
            return

    def update_lesson_status(
        self, lesson_task: LESSONTASK, lesson_status: LESSONSTATUS
    ):
        self.lesson.task = lesson_task
        self.lesson.status = lesson_status

    ## DISPATCH HANDLERS

    def dispatch_dialogue(self, lesson: Lesson):
        job = JobRequest(
            id=self.queue_id,
            task=LESSONTASK.DIALOGUE,
            payload=CPodLessonPayload(
                url=lesson.url,
                slug=lesson.slug,
                lesson_id=lesson.lesson_id,
            ),
        )

        self.cpod_lesson_manager.get_lesson_part(job)

    def dispatch_grammar(self, lesson: Lesson):
        job = JobRequest(
            id=self.queue_id,
            task=LESSONTASK.GRAMMAR,
            payload=CPodLessonPayload(
                url=lesson.url,
                slug=lesson.slug,
                lesson_id=lesson.lesson_id,
            ),
        )

        self.cpod_lesson_manager.get_lesson_part(job)

    def dispatch_vocab(self, lesson: Lesson):
        job = JobRequest(
            id=self.queue_id,
            task=LESSONTASK.VOCAB,
            payload=CPodLessonPayload(
                url=lesson.url,
                slug=lesson.slug,
                lesson_id=lesson.lesson_id,
            ),
        )

        self.cpod_lesson_manager.get_lesson_part(job)

    def dispatch_expansion(self, lesson: Lesson):
        job = JobRequest(
            id=self.queue_id,
            task=LESSONTASK.EXPANSION,
            payload=CPodLessonPayload(
                url=lesson.url,
                slug=lesson.slug,
                lesson_id=lesson.lesson_id,
            ),
        )

        self.cpod_lesson_manager.get_lesson_part(job)

    def dispatch_transcribe_lesson(self, lesson: Lesson):
        # TODO WHISPER SETTINGS From Settings
        if lesson.transcribe_lesson:
            self.ffmpeg_task_manager.whisper_audio(
                JobRequest(
                    id=lesson.queue_id,
                    task=LESSONTASK.TRANSCRIBE,
                    payload=WhisperPayload(
                        provider=WHISPERPROVIDER.WHISPER,
                        file_filename="lesson.mp3",
                        file_folder_path=lesson.storage_path,
                        model_name="tiny",
                    ),
                )
            )

    def dispatch_lesson_audio(self, lesson: Lesson):
        self.audio_download_manager.download_audio(
            job=JobRequest(
                id=lesson.queue_id,
                task=LESSONTASK.LESSON_AUDIO,
                payload=AudioDownloadPayload(
                    audio_urls=lesson.lesson_parts.lesson_audios,
                    export_path=lesson.storage_path,
                    project_name=lesson.title,
                ),
            )
        )

    def dispatch_combine_audio(self, lesson: Lesson):
        self.ffmpeg_task_manager.combine_audio(
            JobRequest(
                id=lesson.queue_id,
                task=LESSONTASK.COMBINE_AUDIO,
                payload=CombineAudioPayload(
                    combine_folder_path=f"{lesson.storage_path}audio",
                    export_file_name="sentences.mp3",
                    export_path=lesson.storage_path,
                    delay_between_audio=1500,
                    project_name=lesson.title,
                ),
            )
        )

    def dispatch_save_lesson(self, lesson: Lesson):
        self.db.write(
            JobRequest(
                id=lesson.queue_id,
                task=LESSONTASK.SAVE_LESSON,
                payload=DBJobPayload(
                    kind=DBJOBTYPE.LESSONS,
                    operation=DBOPERATION.INSERT_ONE,
                    data=InsertOnePayload(data=lesson),
                ),
            )
        )

    def dispatch_check(self, lesson: Lesson):
        job = JobRequest(
            id=self.queue_id,
            task=LESSONTASK.CHECK,
            payload=CPodLessonPayload(
                url=lesson.url,
                slug=lesson.slug,
                lesson_id=lesson.lesson_id,
            ),
        )

        self.cpod_lesson_manager.get_lesson_part(job)

    def dispatch_lesson_parts_audio(self, lesson: Lesson):
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
                    task=LESSONTASK.AUDIO,
                    payload=AudioDownloadPayload(
                        audio_urls=sents_words_with_in_order,
                        export_path=f"{lesson.storage_path}audio",
                        project_name=lesson.title,
                    ),
                )
            )

    def dispatch_lingq_lesson(self, lesson: Lesson):
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
            task=LESSONTASK.LINGQ_LESSON,
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

    def dispatch_lingq_sents(self, lesson: Lesson):
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
                task=LESSONTASK.LINGQ_SENTS,
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

    def dispatch_lingq_dialogue(self, lesson: Lesson):

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
                task=LESSONTASK.LINGQ_DIALOGUE,
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
