class Sentence:
    def __init__(
        self,
        chinese,
        english,
        pinyin,
        audio,
        level="",
        id=0,
        anki_audio=None,
        anki_id=None,
        anki_update=None,
        local_update=None,
    ):
        self.id = id
        self.chinese = chinese
        self.english = english
        self.pinyin = pinyin
        self.level = level
        self.audio = audio
        self.anki_audio = anki_audio
        self.anki_id = anki_id
        self.anki_update = anki_update
        self.local_update = local_update