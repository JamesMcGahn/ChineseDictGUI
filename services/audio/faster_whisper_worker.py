import re
from pathlib import Path

from PySide6.QtCore import Signal, Slot

from base import QWorkerBase
from base.enums import JOBSTATUS
from models.services import FasterWhisperOptions, JobRef, WhisperPayload
from utils.files import PathManager


class FasterWhisperWorker(QWorkerBase):
    task_complete = Signal(object, object)

    def __init__(self, job_ref: JobRef, payload: WhisperPayload):
        super().__init__()
        self.job_ref = job_ref
        self.folder = Path(payload.file_folder_path)
        self.filename = payload.file_filename
        self.language = payload.language
        self.model_name = payload.model_name
        self._stopped = False

        options = payload.options
        if options is None:
            options = FasterWhisperOptions()

        self.compute_type = options.compute_type
        self.beam_size = options.beam_size
        self.min_silence_ms = options.min_silence_ms
        self.chunk_length = options.chunk_length
        self.initial_prompt = payload.initial_prompt
        self.on_previous_text = options.on_previous_text
        self.vad_filter = options.vad_filter
        self.multilingual = options.multilingual

    @Slot()
    def do_work(self):
        try:
            print("in whisper worker")
            audio_exists = PathManager.path_exists(
                f"{self.folder}/{self.filename}", False
            )

            print("in whisper worker", audio_exists)
            if not audio_exists:
                self.logging(
                    f"No audio found in {self.folder}/{self.filename}", "ERROR"
                )
                self.task_complete.emit(
                    JobRef(
                        id=self.job_ref.id,
                        task=self.job_ref.task,
                        status=JOBSTATUS.ERROR,
                    ),
                    {
                        "path": None,
                    },
                )
                self.finished.emit()
                return
            else:
                audio = Path(f"{self.folder}/{self.filename}")

            # # Optionally ensure ffmpeg exists (bundled by imageio-ffmpeg if system ffmpeg missing)
            # try:
            #     import imageio_ffmpeg

            #     os.environ.setdefault(
            #         "IMAGEIO_FFMPEG_EXE", imageio_ffmpeg.get_ffmpeg_exe()
            #     )
            # except Exception:
            #     pass  # If you already have ffmpeg on PATH, that's fine.

            self.logging(f"Loading Whisper model: {self.model_name} …")
            from faster_whisper import WhisperModel

            model = WhisperModel(self.model_name, compute_type=self.compute_type)
            self.logging(f"Whisper model: {self.model_name} Complete.")
            self.logging(f"Starting Transcribing {self.filename}")

            segments, info = model.transcribe(
                str(audio),
                task="transcribe",
                chunk_length=self.chunk_length,
                language=self.language,
                vad_filter=self.vad_filter,
                vad_parameters={"min_silence_duration_ms": self.min_silence_ms},
                condition_on_previous_text=self.vad_filter,
                beam_size=self.beam_size,
                word_timestamps=False,
                initial_prompt=self.initial_prompt,
                multilingual=self.multilingual,
            )

            total = float(info.duration or 0.0)
            buf = []
            last_end = 0.0
            last_logged_pct = 0

            for seg in segments:
                if self._stopped:
                    self.logging("Whisper Process Stopped.", "WARN")
                    self.finished.emit()
                    return

                t = self.normalize_cjk_spacing(seg.text).strip()
                if t:
                    t = self.to_simplified(t)
                    buf.append(t)
                last_end = seg.end or last_end
                if total > 0:
                    frac = min(1.0, last_end / total)
                    percent = int(frac * 100)

                    if percent > last_logged_pct:
                        self.logging(
                            f"{percent}% Percent done - Transcribing {self.filename}"
                        )
                        last_logged_pct = percent
            self.logging(f"Finishing Generating Transcription {self.filename}")
            text = "\n".join(buf) + "\n"
            if not text:
                self.logging("Empty transcript.", "ERROR")
                self.finished.emit()
                return

            out_path = audio.with_suffix(".txt")
            out_path.write_text(text, encoding="utf-8")
            self.logging(f"100% Percent Done - Transcribing {out_path}")
            self.logging(f"Wrote: {out_path.name}")
            self.task_complete.emit(
                JobRef(
                    id=self.job_ref.id,
                    task=self.job_ref.task,
                    status=JOBSTATUS.COMPLETE,
                ),
                {
                    "path": out_path,
                },
            )
            self.finished.emit()

        except Exception as e:
            self.logging(f"{type(e).__name__}: {e}", "ERROR")

    def normalize_cjk_spacing(self, text: str) -> str:
        # Remove stray spaces between CJK chars while keeping English spacing
        pattern = r"(?<!\w)\s+(?=[\u4e00-\u9fff])|(?<=[\u4e00-\u9fff])\s+(?!\w)"
        return re.sub(pattern, "", text)

    def to_simplified(self, text: str) -> str:
        try:
            from opencc import OpenCC

            return OpenCC("t2s").convert(text)  # Traditional → Simplified
        except Exception:
            return text

    @Slot()
    def stop(self) -> None:
        self._stopped = True
