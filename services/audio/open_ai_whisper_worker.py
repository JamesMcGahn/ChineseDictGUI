import json
import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import QProcess, Signal, Slot

from base import QWorkerBase
from services.logger import LOGLEVEL
from utils.files import PathManager


class OpenAIWhisperWorker(QWorkerBase):
    finished = Signal()

    def __init__(self, folder: str, file_name: str, model_name: str = "medium"):
        super().__init__()
        self.folder = Path(folder)
        self.filename = file_name
        self.model_name = "large"
        self.path = None
        self.language = "Mandarin"
        self.audio_length_sec = 0

    def check_path(self, path):
        audio_exists = PathManager.path_exists(path, False)
        print("in whisper worker", audio_exists)

        return audio_exists

    def do_work(self):
        self.path = Path(self.folder, f"{self.filename}.mp3")
        audio_exists = self.check_path(self.path)
        if not audio_exists:
            self.logging(
                f"No audio found in {self.folder}/{self.filename}", LOGLEVEL.ERROR
            )
            self.finished.emit()
            return
        else:
            self.audio_length_sec = self.get_audio_duration(self.path)
            self.process = QProcess(self)
            whisper_exe = Path(sys.executable).with_name("whisper")
            self.process.setProgram(str(whisper_exe))
            self.process.setArguments(
                [
                    str(self.path),
                    "--model",
                    self.model_name,
                    "--language",
                    self.language,
                    "--initial_prompt",
                    "Transcribe Mandarin in Simplified Chinese. Transcribe English in Standard English",
                    "--output_format",
                    "txt",
                    "--output_dir",
                    str(self.folder),
                    "--verbose",
                    "False",
                ]
            )
            self.process.readyReadStandardOutput.connect(self.on_stdout)
            self.process.readyReadStandardError.connect(self.on_stderr)
            self.process.finished.connect(self.on_finished)

            self.process.start()

    @Slot()
    def on_stdout(self):
        text = self.process.readAllStandardOutput().data().decode()
        if text.strip():
            self.logging(text, LOGLEVEL.INFO)

    @Slot()
    def on_stderr(self):
        text = self.process.readAllStandardError().data().decode()

        progress_ts = self.parse_timestamp(text)

        if progress_ts:
            progress_ts = progress_ts.strip()
            self.logging(f"{progress_ts}% Percent done - Transcribing {self.filename}")

        self.logging(f"OpenAI Whisper: {text.strip()}")

    @Slot(int, QProcess.ExitStatus)
    def on_finished(self, code, status):
        if code == 0 and status == QProcess.ExitStatus.NormalExit:
            self.logging(f"100% Percent done - Transcribing {self.filename}")
        self.logging(f"OpenAI has finished with code: {code} - status: {status}")
        self.finished.emit()

    def parse_timestamp(self, ts):
        # Matches timestamps like 00:03.800 or 01:26.480
        parts = ts.split("|")
        if len(parts) >= 3:
            return parts[0][:-1]
        else:
            return None

    def get_audio_duration(self, path: str) -> float:
        print("path", path)
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "quiet",
                "-print_format",
                "json",
                "-show_format",
                f"{str(path)}",
            ],
            capture_output=True,
            text=True,
        )
        info = json.loads(result.stdout)
        print(info)
        return float(info["format"]["duration"])

    @Slot()
    def stop(self):
        if hasattr(self, "process") and self.process.state() != QProcess.NotRunning:
            self.logging("Stopping whisper process...", LOGLEVEL.INFO)
            self.process.kill()
