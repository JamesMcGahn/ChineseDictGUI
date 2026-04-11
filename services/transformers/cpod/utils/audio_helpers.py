import re
from urllib.parse import unquote

from bs4 import Tag

from models.dictionary import Lesson


def build_audio_url_from_api(lesson: Lesson, path: str) -> str:

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


def scrape_audio(element: Tag) -> str:
    audio_table = element.find(class_="jplayer-audio-player")
    if audio_table is None:
        return ""
    audio = audio_table.find("audio")
    if audio and audio.has_attr("src"):
        audio_file = audio["src"]
        # print("audio1", audio_file)
        audio_file = audio_file.replace("http://", "https://")
        # print("audio2", audio_file)
        return audio_file
    else:
        audio_file = unquote(audio_table.find("a", class_="download-link")["href"])
        audio_file = audio_file.replace("/redirect/?url=", "")
        audio_file = audio_file.replace("http://", "https://")
        return audio_file


def clean_audio_link(link: Tag) -> str | None:
    if not link:
        return None

    href = link.get("href")
    if not href:
        return None

    return href.replace("http://", "https://")
