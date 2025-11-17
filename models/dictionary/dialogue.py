class Dialogue:
    def __init__(
        self, title, audio_type, audio, level="", id=0, lesson="", transcribe=True
    ):
        self.id = id
        self.title = title
        self.level = level
        self.audio = audio
        self.audio_type = audio_type
        self.lesson = lesson
        self.transcribe = transcribe
