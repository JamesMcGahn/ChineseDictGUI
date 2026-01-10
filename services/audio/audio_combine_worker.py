import os
import re

from pydub import AudioSegment
from PySide6.QtCore import Signal, Slot

from base import QWorkerBase
from base.enums import JOBSTATUS
from models.services import CombineAudioPayload, JobRef


class AudioCombineWorker(QWorkerBase):
    finished = Signal(str)
    progress = Signal(str)
    task_complete = Signal(object, object)

    def __init__(self, job_ref: JobRef, payload: CombineAudioPayload):
        super().__init__()
        self.job_ref = job_ref
        self.folder_path = payload.combine_folder_path
        self.output_file_name = payload.export_file_name
        self.output_file_folder = payload.export_path
        self.project_name = payload.project_name
        self.silence_ms = payload.delay_between_audio
        self._stopped = False
        self.log_thread()

    def natural_sort_key(self, s: str):
        return [
            int(text) if text.isdigit() else text.lower()
            for text in re.split(r"(\d+)", s)
        ]

    def do_work(self):
        self.log_thread()
        try:
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
                self.finished.emit("")
                return

            combined = AudioSegment.empty()
            spacer = AudioSegment.silent(duration=self.silence_ms)

            for i, filename in enumerate(files):
                if self._stopped:
                    self.logging(
                        f"(Lesson: {self.project_name}) Combine Audio process stopped",
                        "WARN",
                    )
                    self.finished.emit()
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
                f"{self.output_file_folder}{self.output_file_name}",
                format="mp3",
                bitrate="192k",
            )
            self.logging(
                f"(Lesson: {self.project_name}) Saved combined audio to {self.output_file_folder}{self.output_file_name}",
                "INFO",
            )

            self.finished.emit(self.output_file_name)
            self.task_complete.emit(
                JobRef(
                    id=self.job_ref.id,
                    task=self.job_ref.task,
                    status=JOBSTATUS.COMPLETE,
                ),
                {
                    "filename": self.output_file_name,
                    "path": self.output_file_folder,
                    "message": "success",
                },
            )
        except Exception as e:
            self.logging(f"Error in CombineAudioWorker: {e}")
            self.task_complete.emit(
                JobRef(
                    id=self.job_ref.id,
                    task=self.job_ref.task,
                    status=JOBSTATUS.ERROR,
                ),
                {
                    "filename": self.output_file_name,
                    "path": self.output_file_folder,
                    "message": f"{e}",
                },
            )

    @Slot()
    def stop(self) -> None:
        self._stopped = True
