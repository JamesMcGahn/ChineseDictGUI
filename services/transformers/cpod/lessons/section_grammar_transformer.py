from bs4 import BeautifulSoup

from base.enums import EXTRACTDATASOURCE
from models.dictionary import GrammarPoint, Lesson
from services.sentences.models import Sentence
from utils.contains_chinese import contains_chinese

from ....lessons.models import LessonTaskPayload
from ...base_section_transformer import BaseSectionTransformer
from ..utils.audio_helpers import build_audio_url_from_api


class GrammarTransformer(BaseSectionTransformer):

    def __init__(self):
        super().__init__()

    def process_legacy(self, lesson, data):
        sentences = []
        results = []
        soup = BeautifulSoup(data, "html.parser")
        table = soup.find("table")

        if not table:
            return LessonTaskPayload(
                success=False,
                data_source=EXTRACTDATASOURCE.SCRAPE,
            )

        rows = table.find_all("tr")

        current: GrammarPoint = None
        i = 0

        for i, row in enumerate(rows):
            h3 = row.find("h3")
            if h3:
                if current:
                    results.append(current)
                current = GrammarPoint(name=h3.get_text(strip=True), explanation=None)
                continue

            span = row.find("span")
            if span and current:
                current.explanation = span.get_text(strip=True)
                continue

            td = row.find("td")
            text = td.get_text(strip=True)
            if not text:
                continue
            if contains_chinese(text):
                chinese = text
                if i + 2 < len(rows):
                    pinyin_row = rows[i + 1]
                    english_row = rows[i + 2]

                    pinyin = pinyin_row.get_text(strip=True)
                    english = english_row.get_text(strip=True)
                    sentence = Sentence(
                        chinese=chinese,
                        english=english,
                        pinyin=pinyin,
                        audio="",
                        level=lesson.level,
                        sent_type="grammar",
                        lesson=(lesson.title if lesson.title else ""),
                    )
                    sentences.append(sentence)
                    current.examples.append(sentence)

        if current:
            results.append(current)

        return LessonTaskPayload(
            success=True,
            data_source=EXTRACTDATASOURCE.SCRAPE,
            sentences=sentences,
            grammar=results,
        )

    def process_api(self, lesson: Lesson, res_data) -> LessonTaskPayload:
        grammar_points = []
        sentences = []
        if not res_data:
            return LessonTaskPayload(
                success=True,
                data_source=EXTRACTDATASOURCE.API,
            )

        for section in res_data:
            if not isinstance(section, dict) or "grammar" not in section:
                return LessonTaskPayload(
                    success=False,
                    data_source=EXTRACTDATASOURCE.API,
                )
            grammar_point = GrammarPoint(
                name=section["grammar"]["name"],
                explanation=section["grammar"]["introduction"],
            )
            for sentence in section["examples"]:

                audio_path = sentence["audio"]
                audio = build_audio_url_from_api(lesson=lesson, path=audio_path)
                new_sent = Sentence(
                    chinese=sentence["s"],
                    english=sentence["en"],
                    pinyin=sentence["p"],
                    audio=audio,
                    level=lesson.level,
                    sent_type="grammar",
                    lesson=(lesson.title if lesson.title else ""),
                )
                sentences.append(new_sent)
                grammar_point.examples.append(new_sent)
            grammar_points.append(grammar_point)

        return LessonTaskPayload(
            success=True,
            data_source=EXTRACTDATASOURCE.API,
            sentences=sentences,
            grammar=grammar_points,
        )
