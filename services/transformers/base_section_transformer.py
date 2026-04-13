from base import QObjectBase
from base.enums import EXTRACTDATASOURCE
from models.core import LessonTaskPayload
from models.dictionary import Lesson


class BaseSectionTransformer(QObjectBase):

    def __init__(self):
        super().__init__()

        self.source_map = {
            EXTRACTDATASOURCE.API: self.process_api,
            EXTRACTDATASOURCE.SCRAPE: self.process_legacy,
        }

    def detect_source(self, raw_data) -> str:
        self.logging(f"raw data: {raw_data}", "DEBUG", False)

        if isinstance(raw_data, str) and raw_data.strip().startswith("<"):
            return EXTRACTDATASOURCE.SCRAPE
        if isinstance(raw_data, (list, dict)):
            return EXTRACTDATASOURCE.API
        return None

    def process(self, lesson: Lesson, data) -> LessonTaskPayload:
        source = self.detect_source(raw_data=data)
        handler = self.source_map.get(source, None)
        if not handler:
            raise NotImplementedError
        return handler(lesson, data)

    def process_legacy(self, lesson: Lesson, data) -> LessonTaskPayload:
        raise NotImplementedError

    def process_api(self, lesson: Lesson, res_data) -> LessonTaskPayload:
        raise NotImplementedError
