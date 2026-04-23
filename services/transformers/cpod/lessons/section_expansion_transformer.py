from bs4 import BeautifulSoup

from base.enums import EXTRACTDATASOURCE
from models.dictionary import Lesson
from services.sentences.enums import SENTTYPE
from services.sentences.models import Sentence
from utils import strip_string

from ....lessons.models import LessonTaskPayload
from ...base_section_transformer import BaseSectionTransformer
from ..utils.audio_helpers import (
    build_audio_url_from_api,
    scrape_audio,
)


class ExpansionTransformer(BaseSectionTransformer):

    def __init__(self):
        super().__init__()

    def process_legacy(self, lesson, data):
        sentences = []
        soup = BeautifulSoup(data, "html.parser")
        expansion = soup.find(id="expansion")

        if expansion is None:
            return LessonTaskPayload(
                success=False,
                data_source=EXTRACTDATASOURCE.SCRAPE,
                sentences=sentences,
            )

        expand_cards = expansion.find_all("div", class_="cpod-card")

        for card in expand_cards:
            table = card.find_all("tr")
            for sent in table:
                chinese = sent.find("p", class_="click-to-add").get_text()
                pinyin = sent.find("p", class_="show-pinyin").get_text()
                english = sent.find("p", class_="translation-container").get_text()
                audio = scrape_audio(sent)
                pinyin = strip_string(pinyin)
                chinese = strip_string(chinese)
                english = strip_string(english)

                expand_sentence = Sentence(
                    chinese=chinese,
                    english=english,
                    pinyin=pinyin,
                    audio_link=audio,
                    level=lesson.level,
                    sent_type=SENTTYPE.EXPANSION,
                    lesson=(lesson.title if lesson.title else ""),
                )

                sentences.append(expand_sentence)
        return LessonTaskPayload(
            success=True,
            data_source=EXTRACTDATASOURCE.SCRAPE,
            sentences=sentences,
        )

    def process_api(self, lesson: Lesson, res_data) -> LessonTaskPayload:
        sentences = []

        if not res_data:
            return LessonTaskPayload(
                success=True,
                data_source=EXTRACTDATASOURCE.API,
            )

        for section in res_data:
            if not isinstance(section, dict) or "examples" not in section:
                return LessonTaskPayload(
                    success=False,
                    data_source=EXTRACTDATASOURCE.API,
                )
            for sentence in section["examples"]:
                audio_path = sentence["audio"]
                audio = build_audio_url_from_api(lesson=lesson, path=audio_path)
                new_sent = Sentence(
                    chinese=sentence["s"],
                    english=sentence["en"],
                    pinyin=sentence["p"],
                    audio_link=audio,
                    level=lesson.level,
                    sent_type=SENTTYPE.EXPANSION,
                    lesson=(lesson.title if lesson.title else ""),
                )
                sentences.append(new_sent)
        return LessonTaskPayload(
            success=True,
            data_source=EXTRACTDATASOURCE.API,
            sentences=sentences,
        )
