import re
from urllib.parse import urlparse

from base.enums import (
    LESSONLEVEL,
)
from models.dictionary import GrammarPoint, Lesson, Sentence, Word
from services.lessons.models import LessonInfo, LessonTaskPayload


def extract_slug(input_str: str) -> str | None:
    """
    Extracts the slug from a lesson URL or returns the input
    if it's already a slug.

    Supports:
    - https://www.xyz.com/lesson/personal-finances
    - https://www.xyz.com/lessons/personal-finances#dialogue
    - personal-finances
    """

    input_str = re.sub(r"[.,;:!?)]*$", "", input_str)

    # If it's a full URL, parse the path
    if input_str.startswith("http"):
        path = urlparse(input_str).path  # e.g., "/lesson/personal-finances"
        match = re.search(r"/lessons?/([^/?#]+)", path)
        return match.group(1) if match else None

    # If it's already a slug (e.g., "personal-finances")
    if re.fullmatch(r"[a-z0-9\-]+", input_str):
        return input_str

    return None


def parse_lesson_level(raw: str | None) -> LESSONLEVEL | None:
    LEVEL_MAP: dict[str, LESSONLEVEL] = {
        "newbie": LESSONLEVEL.NEWBIE,
        "beginner": LESSONLEVEL.NEWBIE,
        "elementary": LESSONLEVEL.ELEMENTARY,
        "pre intermediate": LESSONLEVEL.PRE_INTERMEDIATE,
        "intermediate": LESSONLEVEL.INTERMEDIATE,
        "upper intermediate": LESSONLEVEL.INTERMEDIATE,
        "advanced": LESSONLEVEL.ADVANCED,
    }
    if raw is None:
        return None
    normalized = raw.strip().lower()
    return LEVEL_MAP.get(normalized)


def build_audio_url(lesson: Lesson, path: str) -> str:

    if path.startswith(
        (
            "https://s3.amazonaws.com",
            "http://s3.amazonaws.com",
            "https://s3contents.chinesepod.com/",
        )
    ):
        return path
    elif "expansionbygrammar" in path:
        match = re.search(r"chinesepod_(\d+)_", path)
        if match:
            grammar_id = match.group(1)
            return f"https://s3contents.chinesepod.com/grammar/grammar_{grammar_id}/{grammar_id}/expansion/translation/mp3/{path}"
        else:
            return ""
    else:
        return f"https://s3contents.chinesepod.com/{lesson.lesson_id}/{lesson.hash_code}/{path}"


def parse_lesson_info(res_data) -> LessonTaskPayload:
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
    return LessonTaskPayload(success=True, lesson_info=lesson_info)


def parse_dialogue(lesson: Lesson, res_data) -> LessonTaskPayload:
    sentences = []
    if "dialogue" in res_data:
        for sentence in res_data["dialogue"]:
            audio_path = sentence["audio"]
            audio = build_audio_url(lesson=lesson, path=audio_path)
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
    return LessonTaskPayload(success=True, sentences=sentences)


def parse_expansion(lesson: Lesson, res_data) -> LessonTaskPayload:
    sentences = []
    if res_data:
        for section in res_data:
            if "examples" not in section:
                continue

            for sentence in section["examples"]:
                audio_path = sentence["audio"]
                audio = build_audio_url(lesson=lesson, path=audio_path)
                new_sent = Sentence(
                    chinese=sentence["s"],
                    english=sentence["en"],
                    pinyin=sentence["p"],
                    audio=audio,
                    level=lesson.level,
                    sent_type="expansion",
                    lesson=(lesson.title if lesson.title else ""),
                )
                sentences.append(new_sent)
    return LessonTaskPayload(success=True, sentences=sentences)


def parse_grammar(lesson: Lesson, res_data) -> LessonTaskPayload:
    grammar_points = []
    sentences = []
    if not res_data:
        return LessonTaskPayload(success=True)

    for section in res_data:
        if not isinstance(section, dict) or "grammar" not in section:
            return LessonTaskPayload(success=False)
        grammar_point = GrammarPoint(
            name=section["grammar"]["name"],
            explanation=section["grammar"]["introduction"],
        )
        for sentence in section["examples"]:

            audio_path = sentence["audio"]
            audio = build_audio_url(lesson=lesson, path=audio_path)
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

    return LessonTaskPayload(success=True, sentences=sentences, grammar=grammar_points)


def parse_vocab(lesson: Lesson, res_data) -> LessonTaskPayload:
    words = []
    if isinstance(res_data, list) and res_data:
        for word in res_data:
            audio_path = word["audio"]
            audio = build_audio_url(lesson=lesson, path=audio_path)
            new_word = Word(
                chinese=word["s"],
                definition=word["en"],
                pinyin=word["p"],
                audio=audio,
                lesson=(lesson.title if lesson.title else ""),
            )
            words.append(new_word)
    return LessonTaskPayload(success=True, words=words)
