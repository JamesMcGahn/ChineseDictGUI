import os
import re

from pydub import AudioSegment
from PySide6.QtCore import Signal, Slot

from base import QWorkerBase
from base.enums import JOBSTATUS
from models.services import (
    CombineAudioPayload,
    CombineAudioResponse,
    JobRef,
    JobRequest,
    JobResponse,
)
from utils.files import PathManager


class AudioCombineWorker(QWorkerBase):
    progress = Signal(str)
    task_complete = Signal(object)

    def __init__(self, job: JobRequest[CombineAudioPayload]):
        super().__init__()
        self.job = job
        self.folder_path = job.payload.combine_folder_path
        self.output_file_name = job.payload.export_file_name
        self.output_file_folder = job.payload.export_path
        self.project_name = job.payload.project_name
        self.silence_ms = job.payload.delay_between_audio
        self.over_write = job.payload.over_write
        self._stopped = False

    def natural_sort_key(self, s: str):
        return [
            int(text) if text.isdigit() else text.lower()
            for text in re.split(r"(\d+)", s)
        ]

    def do_work(self):
        self.log_thread()
        try:
            output_path = os.path.join(self.output_file_folder, self.output_file_name)
            path_exists = PathManager.path_exists(path=output_path, makepath=False)
            if path_exists:
                if self.over_write:
                    os.remove(output_path)
                else:
                    raise FileExistsError(
                        f"{output_path} already exists and overwrite is False"
                    )

            files = [
                f
                for f in os.listdir(self.folder_path)
                if f.lower().endswith((".mp3", ".wav", ".m4a"))
            ]
            files.sort(key=self.natural_sort_key)

            if not files:
                self.logging(
                    f"(Lesson: {self.project_name}) No audio files found.", "WARN"
                )
                self.task_complete.emit(
                    JobResponse(
                        job_ref=JobRef(
                            id=self.job.id,
                            task=self.job.task,
                            status=JOBSTATUS.COMPLETE,
                        ),
                        payload=None,
                    )
                )
                self.done.emit()
                return

            combined = AudioSegment.empty()
            spacer = AudioSegment.silent(duration=self.silence_ms)

            for i, filename in enumerate(files):
                if self._stopped:
                    self.logging(
                        f"(Lesson: {self.project_name}) Combine Audio process stopped",
                        "WARN",
                    )
                    self.task_complete.emit(
                        JobResponse(
                            job_ref=JobRef(
                                id=self.job.id,
                                task=self.job.task,
                                status=JOBSTATUS.COMPLETE,
                            ),
                            payload=None,
                        )
                    )
                    self.done.emit()
                    return

                filepath = os.path.join(self.folder_path, filename)
                self.logging(
                    f"(Lesson: {self.project_name}) Adding {filename} to combined audio file."
                )
                audio = AudioSegment.from_file(filepath)
                combined += audio
                if i < len(files) - 1:
                    combined += spacer

            combined.export(
                output_path,
                format="mp3",
                bitrate="192k",
            )
            self.logging(
                f"(Lesson: {self.project_name}) Saved combined audio to {output_path}",
                "INFO",
            )

            self.task_complete.emit(
                JobResponse(
                    job_ref=JobRef(
                        id=self.job.id,
                        task=self.job.task,
                        status=JOBSTATUS.COMPLETE,
                    ),
                    payload=CombineAudioResponse(
                        filename=self.output_file_name,
                        path=self.output_file_folder,
                        full_path=output_path,
                    ),
                )
            )
            self.done.emit()
        except Exception as e:
            self.logging(f"{e}")
            self.task_complete.emit(
                JobResponse(
                    job_ref=JobRef(
                        id=self.job.id,
                        task=self.job.task,
                        status=JOBSTATUS.ERROR,
                        error=f"{e}",
                    ),
                    payload=None,
                )
            )

    @Slot()
    def stop(self) -> None:
        self._stopped = True
