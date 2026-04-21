from typing import Any

from PySide6.QtCore import QTimer, Signal

from base import QObjectBase, ThreadQueueManager
from base.enums import (
    FAILURESTRATEGY,
    JOBSTATUS,
    LESSONLEVEL,
    LESSONSTATUS,
    LESSONTASK,
    TASKSTATESTATUS,
)
from models.dictionary import Lesson
from models.services import JobRef, JobRequest, JobResponse
from pipelines.actions import (
    EmitUIEventAction,
    FileWriteAction,
    PipelineAction,
)
from pipelines.models import (
    LessonPipelinePayload,
    PipelineServiceContainer,
    TaskDefinition,
    TaskRuntimeState,
)
from services.processors import LessonFileService

# TODO - global registry for processors and transformers
from services.transformers.cpod.utils.lesson_helpers import extract_slug

# TODO ADD STEP ERROR HANDLING


class BaseLessonPipeline(QObjectBase):
    scraping_active = Signal(bool)
    ui_event = Signal(object)
    pipeline_finished = Signal(str)

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
        TASK_GRAPH: dict[LESSONTASK, TaskDefinition] = None

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

        self.writer = LessonFileService()

        self.thread_queue_manager = ThreadQueueManager("Lesson")
        self.base_path = "./test/"

        self.expected_tasks = set()
        self.completed_tasks = set()
        self.queue_id = None
        self.lesson = None

        # TODO get from registry
        self.transformer = None
        self.processor = None

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

        self.dispatchers = {}

        self.action_map = {
            FileWriteAction: self.writer.write_file,
            EmitUIEventAction: self.handle_ui_event_action,
        }

        self.TASK_STATE: dict[LESSONTASK, TaskRuntimeState] = {}

    @property
    def core_tasks(self):
        return getattr(self.Config, "core_tasks", {})

    @property
    def TASK_GRAPH(self):
        tasks = getattr(self.Config, "TASK_GRAPH", None)
        if tasks is None:
            msg = "TASK GRAPH was not added to Pipeline Config"
            self.logging(msg, "ERROR")
            raise NotImplementedError(msg)
        return tasks

    def validate_pipeline_wiring(self):
        graph_tasks = set(self.TASK_GRAPH.keys())
        dispatcher_tasks = set(self.dispatchers.keys())

        missing_dispatchers = graph_tasks - dispatcher_tasks
        extra_dispatchers = dispatcher_tasks - graph_tasks

        if missing_dispatchers:
            msg = f"Missing dispatchers for tasks: {missing_dispatchers}"
            self.logging(msg, "ERROR")
            raise ValueError(msg)

        if extra_dispatchers:
            msg = f"Dispatchers defined for unknown tasks: {extra_dispatchers}"
            self.logging(msg, "ERROR")
            raise ValueError(msg)

    def process(self):
        self.queue_id = self.spec.queue_id
        slug = extract_slug(self.spec.url)
        # TODO: fail if no slug
        self.lesson = Lesson(
            provider=self.spec.provider,
            url=self.spec.url,
            check_dup_sents=self.spec.check_dup_sents,
            check_dup_words=self.spec.check_dup_words,
            transcribe_lesson=self.spec.transcribe_lesson,
            queue_id=self.queue_id,
            slug=slug,
        )
        self.build_expected_tasks(self.spec)
        task = self.get_entry_task()
        self.dispatch(task, self.lesson)

    def get_entry_task(self) -> set[LESSONTASK]:
        return LESSONTASK.INFO

    def job_to_lesson_status(self, job_status: JOBSTATUS):
        try:
            return LESSONSTATUS[job_status.name]
        except KeyError as e:
            if job_status == JOBSTATUS.PARTIAL_ERROR:
                return LESSONSTATUS.ERROR
            else:
                msg = f"Unsupported Job Status: {job_status}"
                self.logging(msg, "ERROR")
                raise ValueError(msg) from e

    def build_expected_tasks(self, spec: LessonPipelinePayload):
        self.expected_tasks.update(self.core_tasks)
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
        state = self._get_task_state(task)
        if state.status in (TASKSTATESTATUS.RUNNING, TASKSTATESTATUS.COMPLETE):
            return
        if dispatcher is None:
            msg = f"No dispatcher defined for task: {task}"
            self.logging(msg, "ERROR")
            raise ValueError(msg)
        state.status = TASKSTATESTATUS.RUNNING
        dispatcher(task=task, lesson=lesson)

    def _get_task_def(self, task: LESSONTASK) -> TaskDefinition:
        return self.TASK_GRAPH.get(task, TaskDefinition())

    def _get_task_state(self, task: LESSONTASK) -> TaskRuntimeState:
        return self.TASK_STATE.setdefault(task, TaskRuntimeState())

    def _get_current_source(self, task: LESSONTASK):
        state = self._get_task_state(task)
        task_def = self._get_task_def(task)
        sources = task_def.sources or []
        if not sources:
            return None
        if state.source_index >= len(sources):
            msg = f"Invalid source index for {task}"
            self.logging(msg, "ERROR")
            raise RuntimeError(msg)
        return sources[state.source_index]

    def _create_job_request(self, queue_id: str, task: LESSONTASK, payload: Any):
        return JobRequest(id=queue_id, task=task, payload=payload)

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

            self.propagate_tasks(job.job_ref.task)

        elif job.job_ref.status == JOBSTATUS.ERROR:
            self.handle_failure(job.job_ref, job.payload, self.lesson)
        else:
            return
        # FEATURE : allow for threshold of number of errors, setting

    def propagate_tasks(self, task: LESSONTASK):
        state = self._get_task_state(task)
        if state.downstream_dispatched:
            return
        next_tasks = self.get_next_tasks(task)
        for task in next_tasks:
            self.dispatch(task, self.lesson)
        state.downstream_dispatched = True

    def handle_success(self, job: JobRef, payload, lesson: Lesson):
        self.update_completed_tasks(job.task)
        state = self._get_task_state(job.task)
        state.status = TASKSTATESTATUS.COMPLETE
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
        msg = f"{type(action)} has not been implemented as an action."
        self.logging(
            msg,
            "ERROR",
        )
        raise NotImplementedError(msg)

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
            state.status = TASKSTATESTATUS.ERROR
            self.propagate_tasks(job.task)

        if policy.failure_strategy == FAILURESTRATEGY.FALLBACK:
            sources = task_def.sources or []
            if state.source_index < len(sources) - 1:
                state.source_index += 1
                state.status = TASKSTATESTATUS.PENDING
                self.logging(
                    f"Retrying {job.task} for {lesson.title} - Falling back to next task source."
                )
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
                state.status = TASKSTATESTATUS.PENDING
                self.logging(
                    f"Retrying {job.task} for {lesson.title} - Attempt: {attempts}/{policy.max_retries}"
                )
                QTimer.singleShot(delay, lambda: self.dispatch(job.task, lesson))
                return
        self.logging(f"{job.task} failed completely", "ERROR")

        state.status = TASKSTATESTATUS.ERROR
        if policy.is_criticial:
            # TODO complete failure
            return
        else:
            self.logging(
                f"Skipping Task {job.task} as it is not critical. Trying to continue"
            )
            state.status = TASKSTATESTATUS.ERROR
            self.propagate_tasks(job.task)
        return

    def update_lesson_status(
        self, lesson_task: LESSONTASK, lesson_status: LESSONSTATUS
    ):
        self.lesson.task = lesson_task
        self.lesson.status = lesson_status

    def check_pipeline_completed(self):

        if self.expected_tasks.issubset(self.completed_tasks):
            self.pipeline_finished.emit(self.queue_id)
        else:
            print("not finished")
            print(self.expected_tasks, self.completed_tasks)

    # TODO
    # def fail_pipeline(self, job: JobRef):
