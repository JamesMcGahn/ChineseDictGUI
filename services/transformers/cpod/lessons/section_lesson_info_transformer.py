from bs4 import BeautifulSoup

from base.enums import EXTRACTDATASOURCE
from models.core import LessonInfo, LessonTaskPayload
from models.dictionary import Lesson

from ...base_section_transformer import BaseSectionTransformer
from ..utils.audio_helpers import clean_audio_link
from ..utils.helpers import parse_lesson_level
from ..utils.lesson_helpers import extract_hash


class LessonInfoTransformer(BaseSectionTransformer):

    def __init__(self):
        super().__init__()

    def process_legacy(self, lesson, data):
        soup = BeautifulSoup(data, "html.parser")

        title_cont = soup.find("h1", class_="lesson-page-title")
        lesson_id = soup.select_one("#v3_id")
        lesson_id = lesson_id.get("value") if lesson_id else None

        badge = title_cont.find("a", class_="badge").get_text()
        title = title_cont.find("span").get_text()
        container = soup.find("div", id="player")

        container = soup.select_one("#panelLessonReviewDownloads")
        if not container:
            return LessonTaskPayload(
                success=False,
                data_source=EXTRACTDATASOURCE.SCRAPE,
                lesson_info=None,
            )

        lesson_link = None
        dialogue_link = None
        for a in container.select("a[href]"):
            text = a.get_text(strip=True)

            # Skip Low Quality version
            if "(LQ)" in text:
                continue

            if text == "Lesson" and not lesson_link:
                lesson_link = clean_audio_link(a)

            elif text == "Dialogue" and not dialogue_link:
                dialogue_link = clean_audio_link(a)

        lesson_info = LessonInfo(
            slug=None,
            lesson_id=lesson_id,
            title=title,
            level=parse_lesson_level(badge),
            hash_code=extract_hash(lesson_link),
            lesson_audio=lesson_link,
            dialogue_audio=dialogue_link,
        )

        return LessonTaskPayload(
            success=True,
            data_source=EXTRACTDATASOURCE.SCRAPE,
            lesson_info=lesson_info,
        )

    def process_api(self, lesson: Lesson, res_data) -> LessonTaskPayload:
        lesson_info = None

        if "hash_code" in res_data and "id" in res_data:
            lesson_info = LessonInfo(
                slug=res_data["slug"],
                lesson_id=res_data["id"],
                title=res_data["title"],
                level=parse_lesson_level(res_data["level"]),
                hash_code=res_data["hash_code"],
                lesson_audio=res_data["mp3_private"],
                dialogue_audio=res_data["mp3_dialogue"],
            )
        else:
            return LessonTaskPayload(
                success=False,
                data_source=EXTRACTDATASOURCE.API,
                lesson_info=lesson_info,
            )
        return LessonTaskPayload(
            success=True,
            data_source=EXTRACTDATASOURCE.API,
            lesson_info=lesson_info,
        )
