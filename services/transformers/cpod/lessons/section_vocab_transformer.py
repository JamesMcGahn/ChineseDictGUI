from bs4 import BeautifulSoup

from base.enums import EXTRACTDATASOURCE
from models.dictionary import Lesson
from services.words.models import Word
from utils import strip_string

from ....lessons.models import LessonTaskPayload
from ...base_section_transformer import BaseSectionTransformer
from ..utils.audio_helpers import build_audio_url_from_api, scrape_audio


class VocabTransformer(BaseSectionTransformer):

    def __init__(self):
        super().__init__()

    def process_legacy(self, lesson, data):
        words = []
        soup = BeautifulSoup(data, "html.parser")
        key_vocab = soup.find(id="key_vocab")
        if key_vocab is None:
            return None

        vocabs = key_vocab.find_all("tr")

        for vocab in vocabs:
            tds = vocab.find_all("td")
            for i, td in enumerate(tds):
                print(f"td[{i}] = {td.get_text(strip=True)}")

            if len(tds) >= 4:
                chinese = tds[1].get_text()
                pinyin = tds[2].get_text()
                define = tds[3].get_text()

                english = strip_string(define)
                chinese = strip_string(chinese)
                chinese = chinese.replace(" ", "")
                pinyin = strip_string(pinyin)
                audio = scrape_audio(vocab)

                new_word = Word(
                    chinese=chinese,
                    definition=english,
                    pinyin=pinyin,
                    audio=audio,
                    lesson=(lesson.title if lesson.title else ""),
                )
                words.append(new_word)
        return LessonTaskPayload(
            success=True,
            data_source=EXTRACTDATASOURCE.SCRAPE,
            words=words,
        )

    def process_api(self, lesson: Lesson, res_data) -> LessonTaskPayload:
        words = []
        if not res_data:
            return LessonTaskPayload(
                success=True,
                data_source=EXTRACTDATASOURCE.API,
            )

        for word in res_data:
            if not isinstance(word, dict) or "s" not in word:
                return LessonTaskPayload(
                    success=False,
                    data_source=EXTRACTDATASOURCE.API,
                )
            audio_path = word["audio"]
            audio = build_audio_url_from_api(lesson=lesson, path=audio_path)
            new_word = Word(
                chinese=word["s"],
                definition=word["en"],
                pinyin=word["p"],
                audio=audio,
                lesson=(lesson.title if lesson.title else ""),
            )
            words.append(new_word)
        return LessonTaskPayload(
            success=True,
            data_source=EXTRACTDATASOURCE.API,
            words=words,
        )
