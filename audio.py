import urllib.request
from random import randint
from time import sleep

import google
from google.cloud import texttospeech
from logger import Logger
from open_file import OpenFile
from write_file import WriteFile


class Audio:
    def __init__(self, path, type):
        self.path = path
        self.type = type
        self.google_tried = False
        self.download_audio()

    def google_audio(self, text, filename):
        try:
            client = texttospeech.TextToSpeechClient.from_service_account_json(
                "./key.json"
            )

            input_text = texttospeech.SynthesisInput(text=text)

            voice = texttospeech.VoiceSelectionParams(
                language_code="cmn-CN",
                name="cmn-CN-Standard-D",
            )

            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            )

            response = client.synthesize_speech(
                request={
                    "input": input_text,
                    "voice": voice,
                    "audio_config": audio_config,
                }
            )
            path = WriteFile.check_dup("./out/audios/words/", filename, ".mp3")

            with open(path, "wb") as out:
                out.write(response.audio_content)
                return True
        except google.api_core.exceptions.ServiceUnavailable as e:
            if self.google_tried is False:
                Logger().insert(
                    "Failed to get Audio From Google...Trying Again...", "WARN"
                )
                sleep(15)
                self.google_tried = True
                self.google_audio(text, filename)
            else:
                Logger().insert("Failed to get Audio From Google", "ERROR")
                Logger().insert(e, "ERROR", False)
                return False

    def download_audio(self):
        data = OpenFile.open_file(self.path, True)
        folder_path = ""
        for i, dat in enumerate(data):
            if self.type == "word":
                folder_path = "./out/audios/words/"

                if dat["audio"] == "":
                    Logger().insert(
                        "No Audio Link in File. Trying to Get Audio from Google...",
                        "INFO",
                    )
                    success = self.google_audio(dat["chinese"], dat["id"])
                    if success:
                        Logger().insert(
                            f'({i+1}/{len(data)}) Audio content written to file "{dat["id"]}.mp3"',
                            "INFO",
                        )
                    continue
            elif self.type == "sentences":
                folder_path = "./out/audios/sentences/"

            path = WriteFile.check_dup(folder_path, dat["id"], ".mp3")
            try:
                urllib.request.urlretrieve(dat["audio"], path)
                Logger().insert(
                    f'({i+1}/{len(data)}) Audio content written to file "{dat["id"]}.mp3"',
                    "INFO",
                )
            except Exception as e:
                Logger().insert(e, "ERROR", False)
                Logger().insert(
                    "Something went wrong...Trying to Get Audio from Google...", "ERROR"
                )
                success = self.google_audio(dat["chinese"], dat["id"])
                if success:
                    Logger().insert(
                        f'({i+1}/{len(data)}) Audio content written to file "{dat["id"]}.mp3"',
                        "INFO",
                    )
            sleep(randint(5, 15))
