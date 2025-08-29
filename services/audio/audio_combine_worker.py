import os
import re

from pydub import AudioSegment
from PySide6.QtCore import Signal

from base import QObjectBase
from services import Logger


class AudioCombineWorker(QObjectBase):
    finished = Signal(str)
    progress = Signal(str)

    def __init__(
        self,
        folder_path: str,
        output_file_name: str,
        output_file_folder: str,
        silence_ms: int = 500,
    ):
        super().__init__()
        self.folder_path = folder_path
        self.output_file_name = output_file_name
        self.output_file_folder = output_file_folder

        self.silence_ms = silence_ms

    def natural_sort_key(self, s: str):
        return [
            int(text) if text.isdigit() else text.lower()
            for text in re.split(r"(\d+)", s)
        ]

    def do_work(self):
        files = [
            f
            for f in os.listdir(self.folder_path)
            if f.lower().endswith((".mp3", ".wav", ".m4a"))
        ]
        files.sort(key=self.natural_sort_key)

        if not files:
            Logger().insert("No audio files found.", "WARN")
            self.finished.emit("")
            return

        combined = AudioSegment.empty()
        spacer = AudioSegment.silent(duration=self.silence_ms)

        for i, filename in enumerate(files):
            filepath = os.path.join(self.folder_path, filename)
            Logger().insert(f"Adding {filename} to combined audio file.")
            audio = AudioSegment.from_file(filepath)
            combined += audio
            if i < len(files) - 1:
                combined += spacer

        combined.export(
            f"{self.output_file_folder}/{self.output_file_name}", format="mp3"
        )
        Logger().insert(
            f"Saved combined audio to {self.output_file_folder}/{self.output_file_name}",
            "INFO",
        )
        self.finished.emit(self.output_file_name)
