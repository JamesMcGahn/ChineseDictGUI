from bs4 import BeautifulSoup

from base.enums import EXTRACTDATASOURCE
from models.dictionary import Lesson, Sentence
from utils import strip_string

from ....lessons.models import LessonTaskPayload
from ...base_section_transformer import BaseSectionTransformer
from ..utils.audio_helpers import (
    build_audio_url_from_api,
    scrape_audio,
)


class DialogueTransformer(BaseSectionTransformer):

    def __init__(self):
        super().__init__()

    def process_legacy(self, lesson: Lesson, data):
        sentences = []
        soup = BeautifulSoup(data, "html.parser")
        dialogue_cont = soup.find("div", id="dialogue")
        if dialogue_cont is None:
            return LessonTaskPayload(
                success=False,
                data_source=EXTRACTDATASOURCE.SCRAPE,
                sentences=sentences,
            )

        dialogue = dialogue_cont.find_all("tr")
        for sentence in dialogue:
            chinese = sentence.find("p", class_="click-to-add").get_text()
            pinyin = sentence.find("p", class_="show-pinyin").get_text()
            english = sentence.find("p", class_="translation-container").get_text()
            audio = scrape_audio(sentence)
            chinese = strip_string(chinese)
            pinyin = strip_string(pinyin)
            english = strip_string(english)

            dialogue_sent = Sentence(
                chinese=chinese,
                english=english,
                pinyin=pinyin,
                audio=audio,
                level=lesson.level,
                sent_type="dialogue",
                lesson=(lesson.title if lesson.title else ""),
            )
            sentences.append(dialogue_sent)
        return LessonTaskPayload(
            success=True,
            data_source=EXTRACTDATASOURCE.SCRAPE,
            sentences=sentences,
        )

    def process_api(self, lesson: Lesson, res_data) -> LessonTaskPayload:
        sentences = []
        if "dialogue" not in res_data:
            return LessonTaskPayload(
                success=False,
                data_source=EXTRACTDATASOURCE.API,
                sentences=sentences,
            )
        for sentence in res_data["dialogue"]:
            audio_path = sentence["audio"]
            audio = build_audio_url_from_api(lesson=lesson, path=audio_path)
            new_sent = Sentence(
                chinese=sentence["s"],
                english=sentence["en"],
                pinyin=sentence["p"],
                audio=audio,
                level=lesson.level,
                sent_type="dialogue",
                lesson=(lesson.title if lesson.title else ""),
            )
            sentences.append(new_sent)
        return LessonTaskPayload(
            success=True,
            data_source=EXTRACTDATASOURCE.API,
            sentences=sentences,
        )
