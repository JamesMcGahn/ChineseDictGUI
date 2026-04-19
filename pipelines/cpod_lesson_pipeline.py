from PySide6.QtCore import Signal

from base import ThreadQueueManager
from base.enums import (
    LESSONLEVEL,
    LESSONTASK,
    PIPELINEJOBTYPE,
)
from models.dictionary import Lesson
from models.pipelines import (
    LessonPipelinePayload,
    PipelineServiceContainer,
    TaskDefinition,
)
from models.services import (
    AudioDownloadPayload,
    CombineAudioPayload,
    CPodLessonPayload,
    LingqLessonPayload,
)
from services.audio.enums import WHISPERPROVIDER
from services.audio.models import WhisperPayload
from services.database.enums import DBJOBTYPE, DBOPERATION
from services.database.models import DBJobPayload
from services.database.models.write import UpsertOnePayload
from services.processors.cpod.cpod_processor_registry import CpodProcessorRegistry

# TODO - global registry for processors and transformers
from services.transformers.cpod.cpod_transformer_registry import CpodTransformerRegistry
from utils.files import PathManager

from .base_lesson_pipeline import BaseLessonPipeline
from .cpod_task_config import TASK_GRAPH as CPOD_TASK_GRAPH

# TODO ADD STEP ERROR HANDLING


class CPodLessonPipeline(BaseLessonPipeline):
    scraping_active = Signal(bool)

    class Config:
        core_tasks = {
            LESSONTASK.INFO,
            LESSONTASK.DIALOGUE,
            LESSONTASK.LESSON_AUDIO,
            LESSONTASK.CHECK,
            LESSONTASK.SAVE_LESSON,
            LESSONTASK.AUDIO,
            LESSONTASK.COMBINE_AUDIO,
        }
        TASK_GRAPH: dict[LESSONTASK, TaskDefinition] = CPOD_TASK_GRAPH

    # TODO SERVICE CONTAINER?
    def __init__(
        self, spec: LessonPipelinePayload, service_cont: PipelineServiceContainer
    ):
        super().__init__(spec=spec, service_cont=service_cont)
        self.spec = spec
        self.cpod_lesson_manager = service_cont.cpod_lesson

        self.transformer = CpodTransformerRegistry().get_transformer(
            PIPELINEJOBTYPE.LESSONS
        )

        self.thread_queue_manager = ThreadQueueManager("Lesson")
        self.base_path = "./test/"

        self.processor = CpodProcessorRegistry().get_processor(PIPELINEJOBTYPE.LESSONS)

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
        self.validate_pipeline_wiring()

    def get_entry_tasks(self) -> set[LESSONTASK]:
        return LESSONTASK.INFO

    ## DISPATCH HANDLERS

    def dispatch_cpod_lesson_part(self, task: LESSONTASK, lesson: Lesson):
        source = self._get_current_source(task)
        job = self._create_job_request(
            self.queue_id,
            task,
            CPodLessonPayload(
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
                job=self._create_job_request(
                    self.queue_id,
                    task,
                    WhisperPayload(
                        provider=WHISPERPROVIDER.WHISPER,
                        file_filename="lesson.mp3",
                        file_folder_path=lesson.storage_path,
                        model_name="tiny",
                    ),
                )
            )

    def dispatch_lesson_audio(self, task: LESSONTASK, lesson: Lesson):
        self.audio_download_manager.download_audio(
            job=self._create_job_request(
                self.queue_id,
                task,
                payload=AudioDownloadPayload(
                    audio_urls=lesson.lesson_parts.lesson_audios,
                    export_path=lesson.storage_path,
                    project_name=lesson.title,
                ),
            )
        )

    def dispatch_combine_audio(self, task: LESSONTASK, lesson: Lesson):
        self.ffmpeg_task_manager.combine_audio(
            job=self._create_job_request(
                self.queue_id,
                task,
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
            job=self._create_job_request(
                self.queue_id,
                task,
                payload=DBJobPayload(
                    kind=DBJOBTYPE.LESSONS,
                    operation=DBOPERATION.UPSERT_ONE,
                    data=UpsertOnePayload(data=lesson),
                ),
            )
        )

    def dispatch_lesson_parts_audio(self, task: LESSONTASK, lesson: Lesson):
        all_sents = lesson.lesson_parts.all_sentences
        words = lesson.lesson_parts.vocab
        # TODO move to Transformer
        sents_words_with_in_order = []
        for i, sent_item in enumerate(all_sents + words):
            sent_item.id = i + 1
            sents_words_with_in_order.append(sent_item)

        if sents_words_with_in_order:
            self.logging(
                f"Adding - {lesson.title} - Sentences & Words Audio to Download Queue."
            )

            self.audio_download_manager.download_audio(
                job=self._create_job_request(
                    self.queue_id,
                    task,
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

        job = self._create_job_request(
            self.queue_id,
            task,
            LingqLessonPayload(
                title=f"{lesson.title} - Lesson",
                collection=collection["lesson"],
                audio_file_name="lesson.mp3",
                audio_file_path=lesson_audio,
                text_file_name="lesson.txt",
                text_file_path=lesson_txt,
                project_name=lesson.title,
            ),
        )

        job_list.append(job)
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
            job = self._create_job_request(
                self.queue_id,
                task,
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

            self.lingq_workflow_manager.create_lingq_lesson(jobs=[job])

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
            job = self._create_job_request(
                self.queue_id,
                task,
                LingqLessonPayload(
                    title=f"{lesson.title} - Dialogue",
                    collection=collection["dialogue"],
                    audio_file_name="dialogue.mp3",
                    audio_file_path=dialogue_audio,
                    text_file_name="dialogue.txt",
                    text_file_path=dialogue_text,
                    project_name=lesson.title,
                ),
            )

            job_list.append(job)

        self.lingq_workflow_manager.create_lingq_lesson(jobs=job_list)
        print("Ready for Lingq")
