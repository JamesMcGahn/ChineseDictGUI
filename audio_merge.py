import os
import re

from pydub import AudioSegment


class AudioCombineWorker:

    def __init__(
        self,
        folder_path: str,
        output_file_name: str,
        output_file_folder: str,
        silence_ms: int = 1000,
        project_name: str = None,
    ):
        super().__init__()
        self.folder_path = folder_path
        self.output_file_name = output_file_name
        self.output_file_folder = output_file_folder
        self.project_name = project_name
        self.silence_ms = silence_ms
        self._stopped = False

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
            return
        print(len(files))
        count = 1
        batch = []
        batches = []

        for i, file in enumerate(files):
            if count == 101:
                print(f"batch {i} - finished", len(batch))
                batches.append(batch)
                count = 1
                batch = []
            batch.append(file)
            count += 1
        batches.append(batch)
        print(len(batches))
        print([len(batch) for batch in batches])
        for j, batch in enumerate(batches):
            combined = AudioSegment.empty()
            spacer = AudioSegment.silent(duration=self.silence_ms)
            for i, filename in enumerate(batch):
                if self._stopped:
                    return
                print(f"Batch {j+1}: {filename}")
                filepath = os.path.join(self.folder_path, filename)

                audio = AudioSegment.from_file(filepath)
                combined += audio
                if i < len(batch) - 1:
                    combined += spacer

            combined.export(
                f"{self.output_file_folder}/{j+1:02d}-{self.output_file_name}",
                format="mp3",
                bitrate="192k",
            )


a = AudioCombineWorker(
    "test/Lili and Zhang Liang 15: Uncomfortable Encounter in a Bar/sents",
    "sentences.mp3",
    "test/Lili and Zhang Liang 15: Uncomfortable Encounter in a Bar/",
)
a.do_work()
