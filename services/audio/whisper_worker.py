import re
from pathlib import Path

from PySide6.QtCore import Slot

from base import QWorkerBase
from utils.files import PathManager


class WhisperWorker(QWorkerBase):

    def __init__(self, folder: str, file_name: str, model_name: str = "medium"):
        super().__init__()
        self.folder = Path(folder)
        self.filename = file_name
        self.language = "zh"
        self.model_name = model_name
        self._stopped = False
        self.model_name = "large"
        self.compute_type = "auto"
        self.beam_size = 8
        self.min_silence_ms = 2500
        self.chunk_length = 120

        if any(
            level in file_name
            for level in ["Newbie", "Elementary", "Pre-Intermediate", "Intermediate"]
        ):
            self.initial_prompt = """
                "Transcribe Mandarin in Simplified Chinese. Transcribe English in Standard English"
            """
        else:
            self.initial_prompt = (
                "Transcribe Mandarin using Simplified Chinese characters. "
            )

    @Slot()
    def do_work(self):
        try:
            print("in whisper worker")
            audio_exists = PathManager.path_exists(
                f"{self.folder}/{self.filename}.mp3", False
            )

            print("in whisper worker", audio_exists)
            if not audio_exists:
                self.logging(
                    f"No audio found in {self.folder}/{self.filename}", "ERROR"
                )
                self.finished.emit()
                return
            else:
                audio = Path(f"{self.folder}/{self.filename}.mp3")

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
                vad_filter=False,
                vad_parameters={"min_silence_duration_ms": self.min_silence_ms},
                condition_on_previous_text=True,
                beam_size=self.beam_size,
                word_timestamps=False,
                initial_prompt=self.initial_prompt,
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
            self.logging(f"100% Percent Done - Transcribing {self.filename}")
            self.logging(f"Wrote: {out_path.name}")
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
