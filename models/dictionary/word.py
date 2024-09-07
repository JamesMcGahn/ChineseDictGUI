class Word:
    def __init__(
        self,
        chinese,
        definition,
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
        self.pinyin = pinyin
        self.definition = definition
        self.audio = audio
        self.level = level
        self.anki_audio = anki_audio
        self.anki_id = anki_id
        self.anki_update = anki_update
        self.local_update = local_update