from .enums import LESSONPROVIDERS
from .models import LessonWorkFlowRequest


class LessonRequestBuilder:

    def build_request_from_text(
        self,
        text: str,
        check_for_dup_sents: bool,
        check_for_dup_words: bool,
        transcribe_lesson: bool,
    ):
        requests = []
        for url in text:
            url = url.strip()
            if not url:
                continue

            if "chinesepod" in url:
                requests.append(
                    LessonWorkFlowRequest(
                        provider=LESSONPROVIDERS.CPOD,
                        url=url,
                        slug=None,
                        check_dup_sents=check_for_dup_sents,
                        check_dup_words=check_for_dup_words,
                        transcribe_lesson=transcribe_lesson,
                    )
                )
        return requests
