import uuid

from PySide6.QtCore import QThread, Signal

from base import QObjectBase, ThreadQueueManager
from base.enums import (
    DBJOBTYPE,
    DBOPERATION,
    JOBSTATUS,
    LESSONAUDIO,
    LESSONLEVEL,
    LESSONSTATUS,
    LESSONTASK,
    WHISPERPROVIDER,
)
from core.scrapers.cpod.lessons import LessonScraperThread
from models.core import LessonTaskPayload
from models.dictionary import Lesson, LessonAudio, Sentence, Word
from models.services import (
    AudioDownloadPayload,
    CombineAudioPayload,
    JobItem,
    JobRef,
    LingqLessonPayload,
    WhisperPayload,
)
from models.services.database import DBJobPayload
from models.services.database.write import InsertOnePayload
from services.network import TokenManager
from utils.files import PathManager

from .audio_download_manager import AudioDownloadManager
from .database_service_manager import DatabaseServiceManager
from .ffmpeg_task_manager import FFmpegTaskManager
from .lingq_workflow_manager import LingqWorkFlowManager


# TODO move logic to pipeline
class LessonWorkFlowManager(QObjectBase):
    scraping_active = Signal(bool)
    send_sents_sig = Signal(list, bool)
    send_words_sig = Signal(list, bool)

    def __init__(
        self,
        audio_download_manager: AudioDownloadManager,
        ffmeg_task_manager: FFmpegTaskManager,
        lingq_workflow_manager: LingqWorkFlowManager,
        db: DatabaseServiceManager,
    ):
        super().__init__()
        self.ffmeg_task_manager = ffmeg_task_manager
        self.audio_download_manager = audio_download_manager
        self.lingq_workflow_manager = lingq_workflow_manager
        self.db = db
        self.lesson_threads = []
        self.token_manager = TokenManager()
        self.lessons_queue: dict[str, Lesson] = {}
        self.thread_queue_manager = ThreadQueueManager("Lesson")
        self.base_path = "./test/"
        # self.thread_queue_manager.thread_running.connect(self.scraping_active)
        # combine_folder_path=f"./test/Newbie/Do You Like Shanghai?/audio",
        # export_file_name="sentences.mp3",
        # export_path="./test/Newbie/Do You Like Shanghai?/",
        # delay_between_audio=1500,
        # project_name="test",

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

        self.success_task_handlers = {
            LESSONTASK.AUDIO: self.combine_audio,
            LESSONTASK.INFO: self.process_lesson_info,
            LESSONTASK.LESSON_AUDIO: self.transcribe_lesson,
            LESSONTASK.DIALOGUE: self.process_dialogue,
            LESSONTASK.VOCAB: self.process_vocab,
            LESSONTASK.EXPANSION: self.process_expansion,
            LESSONTASK.GRAMMAR: self.process_grammar,
            LESSONTASK.CHECK: self.save_lesson,
            LESSONTASK.TRANSCRIBE: self.transcription_ready_for_lingq,
            LESSONTASK.COMBINE_AUDIO: self.lesson_parts_ready_for_lingq,
        }

    def create_lesson_scrape(self, lesson_specs):
        jobs = []
        for spec in lesson_specs:
            queue_id = uuid.uuid4()
            # TODO change to data model
            add_lesson = Lesson(
                provider=spec["provider"],
                url=spec["url"],
                check_dup_sents=spec["check_dup_sents"],
                transcribe_lesson=spec["transcribe_lesson"],
                queue_id=queue_id,
                slug="",
            )

            new_spec = {
                "provider": "cpod",
                "slug": "",
                "queue_id": queue_id,
                "url": spec["url"],
                "check_dup_sents": spec["check_dup_sents"],
                "transcribe_lesson": spec["transcribe_lesson"],
            }

            self.lessons_queue[queue_id] = add_lesson
            jobs.append(new_spec)

        lesson_thread = LessonScraperThread(jobs)
        lesson_thread.request_token.connect(self.token_manager.request_token)
        lesson_thread.task_complete.connect(self.on_task_completed)
        self.token_manager.send_token.connect(lesson_thread.receive_token)
        self.lesson_threads.append(lesson_thread)
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

    # TODO Clean up - > move code to methods
    def on_task_completed(self, job: JobRef, payload):
        print("here", job)
        if job.id not in self.lessons_queue:
            return

        lesson: Lesson = self.lessons_queue[job.id]

        self.update_lesson_status(
            job.id, job.task, self.job_to_lesson_status(job.status)
        )

        if lesson is None:
            return

        # if job.task == LESSONTASK.LESSON_AUDIO and job.status == JOBSTATUS.COMPLETE:
        #     if lesson.transcribe_lesson:
        #         self.ffmeg_task_manager.whisper_audio(
        #             lesson.storage_path, LESSONAUDIO.LESSON
        #         )

        if job.status == JOBSTATUS.COMPLETE:
            self.handle_success(job, payload, lesson)
        elif job.status == JOBSTATUS.ERROR:
            self.handle_failure(job, payload, lesson)
        else:
            return
        # FEATURE : allow for threshold of number of errors, setting

    def handle_success(self, job: JobRef, payload, lesson: Lesson):
        handler = self.success_task_handlers.get(job.task)

        if handler:
            handler(lesson, payload)

    def handle_failure(self, job, payload, lesson):
        self.logging(f"{job.task} failed for {lesson.title}", "ERROR")
        lesson.status = LESSONSTATUS.ERROR

    def update_lesson_status(
        self, queue_id, lesson_task: LESSONTASK, lesson_status: LESSONSTATUS
    ):
        if queue_id not in self.lessons_queue:
            return
        lesson = self.lessons_queue[queue_id]
        lesson.task = lesson_task
        lesson.status = lesson_status

    def combine_audio(self, lesson: Lesson, payload):
        self.ffmeg_task_manager.combine_audio(
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

    def process_lesson_info(self, lesson: Lesson, payload: LessonTaskPayload):
        lesson_info = payload.lesson_info

        lesson.hash_code = lesson_info.hash_code
        lesson.level = lesson_info.level
        lesson.lesson_id = lesson_info.lesson_id
        lesson.title = lesson_info.title
        lesson.slug = lesson_info.slug

        path = f"{self.base_path}{lesson.level}/{lesson.title}/"
        lesson.storage_path = path

        dialogue_audio = LessonAudio(
            title="dialogue",
            audio_type=LESSONAUDIO.DIALOGUE,
            audio=lesson_info.dialogue_audio,
            level=lesson.level,
            lesson=lesson.title,
            transcribe=False,
        )

        lesson_audio = LessonAudio(
            title="lesson",
            audio_type=LESSONAUDIO.LESSON,
            audio=lesson_info.lesson_audio,
            level=lesson.level,
            lesson=lesson.title,
            transcribe=lesson.transcribe_lesson,
        )
        lesson.lesson_parts.lesson_audios.append(dialogue_audio)
        lesson.lesson_parts.lesson_audios.append(lesson_audio)

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

    def transcribe_lesson(self, lesson: Lesson, payload):
        # TODO WHISPER SETTINGS From Settings
        if lesson.transcribe_lesson:
            self.ffmeg_task_manager.whisper_audio(
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

    def process_dialogue(self, lesson: Lesson, payload: LessonTaskPayload):
        dialogue = payload.sentences
        if not dialogue:
            return
        lesson.lesson_parts.dialogue = dialogue
        lesson.lesson_parts.all_sentences.extend(dialogue)
        PathManager.path_exists(lesson.storage_path, True)
        self.send_sents_sig.emit(dialogue, lesson.check_dup_sents)
        with open(
            f"{lesson.storage_path}dialogue.txt",
            "w",
            encoding="utf-8",
        ) as f:
            for sent in dialogue:
                f.write(f"{sent.chinese}\n")

    def process_vocab(self, lesson: Lesson, payload: LessonTaskPayload):
        words = payload.words
        lesson.lesson_parts.vocab = words
        self.send_words_sig.emit(words, False)

    def process_expansion(self, lesson: Lesson, payload: LessonTaskPayload):
        expansion = payload.sentences
        lesson.lesson_parts.expansion = expansion
        lesson.lesson_parts.all_sentences.extend(expansion)
        self.send_sents_sig.emit(expansion, lesson.check_dup_sents)

    def process_grammar(self, lesson: Lesson, payload: LessonTaskPayload):
        grammar_points = payload.grammar
        sentences = payload.sentences
        lesson.lesson_parts.grammar = grammar_points
        lesson.lesson_parts.all_sentences.extend(sentences)
        self.send_sents_sig.emit(sentences, lesson.check_dup_sents)

    def transcription_ready_for_lingq(self, lesson: Lesson, payload):
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

    def lesson_parts_ready_for_lingq(self, lesson: Lesson, payload):
        sents_text = f"{lesson.storage_path}sentences.txt"
        sents_audio = f"{lesson.storage_path}sentences.mp3"
        dialogue_text = f"{lesson.storage_path}dialogue.txt"
        dialogue_audio = f"{lesson.storage_path}dialogue.mp3"

        sents_audio_exists = PathManager.path_exists(
            path=sents_audio,
            makepath=False,
        )

        sents_txt_exists = PathManager.path_exists(
            path=sents_text,
            makepath=False,
        )

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
        if sents_audio_exists and sents_txt_exists:
            sents = JobItem[LingqLessonPayload](
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
            job_list.append(sents)

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

    def save_lesson(self, lesson: Lesson, payload):
        all_sents = lesson.lesson_parts.all_sentences
        words = lesson.lesson_parts.vocab
        dialogue = lesson.lesson_parts.dialogue
        lesson_audios = lesson.lesson_parts.lesson_audios

        PathManager.path_exists(lesson.storage_path, True)

        with open(f"{lesson.storage_path}sentences.txt", "w", encoding="utf-8") as f:
            if lesson.lesson_parts.dialogue:
                f.write("对话:\n")
                for sent in lesson.lesson_parts.dialogue:
                    f.write(f"{sent.chinese}\n")

            if lesson.lesson_parts.expansion:
                f.write("例句:\n")
                for sent in lesson.lesson_parts.expansion:
                    f.write(f"{sent.chinese}\n")

            if lesson.lesson_parts.grammar:
                f.write("语法:\n")
                for grammar_point in lesson.lesson_parts.grammar:
                    f.write(f"{grammar_point.name}\n")
                    f.write(f"{grammar_point.explanation}\n")
                    for sent in grammar_point.examples:
                        f.write(f"{sent.chinese}\n")

            if lesson.lesson_parts.vocab:
                f.write("词汇:\n")
                for word in lesson.lesson_parts.vocab:
                    f.write(f"{word.chinese}\n")

        sents_words_with_in_order = []
        for i, sent_item in enumerate(all_sents + words):
            sent_item.id = i + 1
            sents_words_with_in_order.append(sent_item)
            # return  # TODO REMOVE AFTER TESTING WHISPER
            # TODO add an option to disable downloading all sentences for lesson

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

            # combine_audio=False,
            # combine_audio_export_folder=path,
            # combine_audio_export_filename="Sentences.mp3",
            # combine_audio_delay_between_audio=1500,
