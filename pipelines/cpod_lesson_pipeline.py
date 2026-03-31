from typing import TYPE_CHECKING

from .base_pipeline import BaseLessonPipeline

if TYPE_CHECKING:
    from services.managers import (
        AudioDownloadManager,
        FFmpegTaskManager,
        LingqWorkFlowManager,
        DatabaseServiceManager,
    )

from PySide6.QtCore import Signal

from base import ThreadQueueManager
from base.enums import (
    DBJOBTYPE,
    DBOPERATION,
    JOBSTATUS,
    LESSONLEVEL,
    LESSONSTATUS,
    LESSONTASK,
    WHISPERPROVIDER,
)
from core.scrapers.cpod.lessons import LessonScraperThread
from models.dictionary import Lesson
from models.pipelines import (
    EmitUIEventAction,
    FileWriteAction,
    LessonPipelinePayload,
    PipelineAction,
)
from models.services import (
    AudioDownloadPayload,
    CombineAudioPayload,
    CPodLessonPayload,
    JobItem,
    JobRef,
    LingqLessonPayload,
    WhisperPayload,
)
from models.services.database import DBJobPayload
from models.services.database.write import InsertOnePayload
from services.lessons import LessonFileService
from services.lessons.processors.cpod import CpodLessonProcessor
from services.network import TokenManager
from utils.files import PathManager

# TODO ADD STEP ERROR HANDLING


class CPodLessonPipeline(BaseLessonPipeline):
    scraping_active = Signal(bool)

    # TODO SERVICE CONTAINER?
    def __init__(
        self,
        spec: LessonPipelinePayload,
        audio_download_manager: "AudioDownloadManager",
        ffmpeg_task_manager: "FFmpegTaskManager",
        lingq_workflow_manager: "LingqWorkFlowManager",
        db: "DatabaseServiceManager",
    ):
        super().__init__()
        self.spec = spec
        self.ffmpeg_task_manager = ffmpeg_task_manager
        self.audio_download_manager = audio_download_manager
        self.lingq_workflow_manager = lingq_workflow_manager
        self.db = db

        self.token_manager = TokenManager()
        self.thread_queue_manager = ThreadQueueManager("Lesson")
        self.base_path = "./test/"

        self.expected_tasks = set()
        self.completed_tasks = set()
        self.queue_id = None
        self.lesson = None
        self.processor = CpodLessonProcessor()
        self.writer = LessonFileService()

        self.ffmpeg_task_manager.task_complete.connect(self.on_task_completed)
        self.audio_download_manager.task_complete.connect(self.on_task_completed)
        self.db.task_complete.connect(self.on_task_completed)
        self.lingq_workflow_manager.task_complete.connect(self.on_task_completed)

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
            LESSONTASK.INFO: [LESSONTASK.LESSON_AUDIO],
            LESSONTASK.CHECK: [LESSONTASK.SAVE_LESSON, LESSONTASK.AUDIO],
            LESSONTASK.AUDIO: [LESSONTASK.COMBINE_AUDIO],
            LESSONTASK.TRANSCRIBE: [LESSONTASK.LINGQ_LESSON],
            LESSONTASK.LESSON_AUDIO: [LESSONTASK.TRANSCRIBE, LESSONTASK.LINGQ_DIALOGUE],
            LESSONTASK.COMBINE_AUDIO: [LESSONTASK.LINGQ_SENTS],
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
        }

        self.action_map = {
            FileWriteAction: self.writer.write_file,
            EmitUIEventAction: self.handle_ui_event_action,
        }

    def process(self):

        self.queue_id = self.spec.queue_id
        self.lesson = Lesson(
            provider=self.spec.provider,
            url=self.spec.url,
            check_dup_sents=self.spec.check_dup_sents,
            transcribe_lesson=self.spec.transcribe_lesson,
            queue_id=self.queue_id,
            slug="",
        )
        self.build_expected_tasks(self.spec)

        job = JobItem(
            id=self.queue_id,
            task=LESSONTASK.INFO,
            payload=CPodLessonPayload(url=self.spec.url),
        )

        lesson_thread = LessonScraperThread([job])
        lesson_thread.request_token.connect(self.token_manager.request_token)
        lesson_thread.task_complete.connect(self.on_task_completed)
        self.token_manager.send_token.connect(lesson_thread.receive_token)

        lesson_thread.finished.connect(
            lambda: self.thread_queue_manager.on_finished_thread(lesson_thread)
        )
        self.thread_queue_manager.add_thread(lesson_thread)

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

    def on_task_completed(self, job: JobRef, payload):
        print("here", job)
        if job.id != self.queue_id or self.lesson is None:
            return

        self.update_lesson_status(job.task, self.job_to_lesson_status(job.status))
        if job.status == JOBSTATUS.COMPLETE:

            self.handle_success(job, payload, self.lesson)

            next_tasks = self.get_next_tasks(job.task)
            for task in next_tasks:
                self.dispatch(task, self.lesson)

        elif job.status == JOBSTATUS.ERROR:
            self.handle_failure(job, payload, self.lesson)
        else:
            return
        # FEATURE : allow for threshold of number of errors, setting

    def handle_success(self, job: JobRef, payload, lesson: Lesson):
        self.update_completed_tasks(job.task)
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

    def handle_failure(self, job, payload, lesson):
        self.logging(f"{job.task} failed for {lesson.title}", "ERROR")
        lesson.status = LESSONSTATUS.ERROR

    def update_lesson_status(
        self, lesson_task: LESSONTASK, lesson_status: LESSONSTATUS
    ):
        self.lesson.task = lesson_task
        self.lesson.status = lesson_status

    ## DISPATCH HANDLERS

    def dispatch_transcribe_lesson(self, lesson: Lesson):
        # TODO WHISPER SETTINGS From Settings
        if lesson.transcribe_lesson:
            self.ffmpeg_task_manager.whisper_audio(
                job_ref=JobRef(
                    lesson.queue_id, LESSONTASK.TRANSCRIBE, JOBSTATUS.CREATED
                ),
                payload=WhisperPayload(
                    provider=WHISPERPROVIDER.WHISPER,
                    file_filename="lesson.mp3",
                    file_folder_path=lesson.storage_path,
                    model_name="tiny",
                ),
            )

    def dispatch_lesson_audio(self, lesson: Lesson):
        self.audio_download_manager.download_audio(
            job=JobItem(
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
            job_ref=JobRef(
                lesson.queue_id, LESSONTASK.COMBINE_AUDIO, JOBSTATUS.CREATED
            ),
            payload=CombineAudioPayload(
                combine_folder_path=f"{lesson.storage_path}audio",
                export_file_name="sentences.mp3",
                export_path=lesson.storage_path,
                delay_between_audio=1500,
                project_name=lesson.title,
            ),
        )

    def dispatch_save_lesson(self, lesson: Lesson):
        self.db.write(
            JobItem(
                id=lesson.queue_id,
                task=LESSONTASK.SAVE_LESSON,
                payload=DBJobPayload(
                    kind=DBJOBTYPE.LESSONS,
                    operation=DBOPERATION.INSERT_ONE,
                    data=InsertOnePayload(data=lesson),
                ),
            )
        )

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
                JobItem(
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

        lesson = JobItem[LingqLessonPayload](
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
            lingq_sent = JobItem[LingqLessonPayload](
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
            dialogue = JobItem[LingqLessonPayload](
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
