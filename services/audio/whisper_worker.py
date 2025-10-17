import re
from pathlib import Path

from PySide6.QtCore import Signal, Slot

from base import QObjectBase
from utils.files import PathManager


class WhisperWorker(QObjectBase):
    finished = Signal()

    def __init__(self, folder: str, file_name: str, model_name: str = "medium"):
        super().__init__()
        self.folder = Path(folder)
        self.filename = file_name
        self.language = "zh"
        self.model_name = model_name
        self._stopped = False
        self.model_name = "medium"
        self.compute_type = "auto"
        self.beam_size = 5
        self.min_silence_ms = 300
        self.chunk_length = 45
        self.initial_prompt = (
            "这是一段包含中文和英文的课程音频。仅转写所听内容，不要翻译。"
            "中文请按普通话（现代标准汉语）规范转写，使用简体中文；不要繁体、不要拼音，汉字之间不要加空格。"
            "如有歧义，优先采用普通话用词与写法，不要使用方言或粤语字。"
            "英文保持英文原文，并使用正常标点；中英文之间保留一个空格。"
            "不要添加时间戳、说话人或额外说明。"
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
                vad_filter=True,
                vad_parameters={"min_silence_duration_ms": self.min_silence_ms},
                condition_on_previous_text=False,
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
