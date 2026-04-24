from collections import deque
from random import randint

from PySide6.QtCore import QTimer, Signal, Slot

from base import QWorkerBase
from base.enums import JOBSTATUS
from models.services import (
    BatchJobResponse,
    JobRef,
    JobRequest,
    JobResponse,
)
from utils.files import PathManager

from ..models import AudioDownloadPayload
from ..models.audio_download_validate import AudioDLValidationResult
from .retryable_audio_error import RetryableAudioError


class BaseAudioDLProvider(QWorkerBase):
    task_complete = Signal(object)

    def __init__(self, job: JobRequest[AudioDownloadPayload]):
        super().__init__()
        self.job = job
        self.data = deque(job.payload.audio_urls)
        self.project_name = job.payload.project_name

        self._stopped = False
        self.queue_downloading = False

        self.count = 0
        self.data_length = len(self.data)
        self.download_success = 0
        self.download_error = 0

        self.current_item = None
        self.failed_items = []
        self.succeed_items = []

        self.retried_download = False

    class Config:
        has_config = False
        provider_name = "provider"

    @property
    def has_config(self):
        return getattr(self.Config, "has_config", False)

    @property
    def provider_name(self):
        return getattr(self.Config, "provider_name", "provider")

    def setup_config(self):
        msg = f"setup_config has not been implemented by {self.__class__.__name__}"
        self.logging(msg, "ERROR")
        raise NotImplementedError(msg)

    def validate_check(self) -> AudioDLValidationResult:
        msg = f"validate_check has not been implemented by {self.__class__.__name__}"
        self.logging(msg, "ERROR")
        raise NotImplementedError(msg)

    def process_audio(self, path: str):
        msg = f"process_audio has not been implemented by {self.__class__.__name__}"
        self.logging(msg, "ERROR")
        raise NotImplementedError(msg)

    def do_work(self):
        self.log_thread()
        if self.has_config:
            self.setup_config()
        QTimer.singleShot(0, self.download_next_audio)

    def schedule_next_download(self):
        if not self.data:
            self.check_done()
        elif self._stopped:
            self.logging("Audio Download Process Stopped.", "WARN")
            self.done.emit()
        else:
            wait_time = randint(5, 20)
            self.logging(f"Waiting {wait_time} seconds before next audio download")

            QTimer.singleShot(wait_time * 1000, self.download_next_audio)

    def download_next_audio(self):
        if not self.data:
            self.check_done()
            return
        self.queue_downloading = True
        try:
            self.current_item = self.data.popleft()

            valid_result = self.validate_check()
            if valid_result.fatal:
                self.complete_failure(valid_result.message)
                return
            elif not valid_result.ok:
                self.on_error(valid_result.message)
                return

            path = PathManager.check_dup(
                self.current_item.target_path, self.current_item.file_name, ".mp3"
            )
            self.process_audio(path)
            success_msg = f'({self.project_name} - {self.count + 1}/{self.data_length}) Audio content written to file "{self.current_item.file_name}.mp3"'
            self.logging(success_msg, "INFO")
            self.retried_download = False
            self.count += 1
            self.download_success += 1
            self.succeed_items.append(self.current_item)
            QTimer.singleShot(0, self.schedule_next_download)
        except RetryableAudioError as e:
            self.maybe_try_again(e, e.backoff)
        except Exception as e:
            self.maybe_try_again(e)
        finally:
            self.queue_downloading = False

    def send_finished(self):
        self.done.emit()

    def maybe_try_again(self, e, back_off_time=15):
        if self.retried_download:
            self.on_error(e)
            return
        backoff_time = 1000 * back_off_time
        failure_msg_retry = f"({self.project_name} - {self.current_item.file_name}.mp3) - Failed to download audio from {self.provider_name}...Trying Again in {back_off_time} secs..."
        self.logging(failure_msg_retry, "WARN")

        self.retried_download = True
        self.data.appendleft(self.current_item)
        QTimer.singleShot(backoff_time, self.schedule_next_download)

    def check_done(self):
        if not self.data and not self.queue_downloading:

            self.logging(
                f"{self.project_name} - Finished Downloading Audio - Success: {self.download_success} Failure: {self.download_error}"
            )

            if self.download_error == 0:
                status = JOBSTATUS.COMPLETE
            elif self.download_success == 0:
                status = JOBSTATUS.ERROR
            else:
                status = JOBSTATUS.PARTIAL_ERROR

            self.task_complete.emit(
                JobResponse(
                    job_ref=JobRef(id=self.job.id, task=self.job.task, status=status),
                    payload=BatchJobResponse(
                        success_count=self.download_success,
                        error_count=self.download_error,
                        total_count=self.data_length,
                        failed_items=self.failed_items,
                        data=self.succeed_items,
                    ),
                )
            )
            self.done.emit()

    def on_error(self, e):
        self.download_error += 1
        self.logging(
            f"({self.project_name} - {self.current_item.file_name}.mp3) - Failed to download audio from {self.provider_name}.",
            "ERROR",
        )
        self.logging(f"{e}", "DEBUG", False)
        self.failed_items.append(self.current_item)
        QTimer.singleShot(0, self.schedule_next_download)

    def complete_failure(self, msg):
        status = JOBSTATUS.ERROR
        self.task_complete.emit(
            JobResponse(
                job_ref=JobRef(
                    id=self.job.id, task=self.job.task, status=status, error=msg
                ),
                payload=BatchJobResponse(
                    success_count=0,
                    error_count=self.data_length,
                    total_count=self.data_length,
                    failed_items=[self.current_item, *self.data],
                    data=[self.current_item, *self.data],
                ),
            )
        )
        self.done.emit()

    @Slot()
    def stop(self) -> None:
        self._stopped = True
