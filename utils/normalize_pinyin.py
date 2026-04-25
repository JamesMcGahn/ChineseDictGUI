import re
import unicodedata

TONE_MARK_MAP = {
    "ā": "a1",
    "á": "a2",
    "ǎ": "a3",
    "à": "a4",
    "ē": "e1",
    "é": "e2",
    "ě": "e3",
    "è": "e4",
    "ī": "i1",
    "í": "i2",
    "ǐ": "i3",
    "ì": "i4",
    "ō": "o1",
    "ó": "o2",
    "ǒ": "o3",
    "ò": "o4",
    "ū": "u1",
    "ú": "u2",
    "ǔ": "u3",
    "ù": "u4",
    "ǖ": "v1",
    "ǘ": "v2",
    "ǚ": "v3",
    "ǜ": "v4",
    "ü": "v",
}


def normalize_pinyin(text: str) -> str:
    text = unicodedata.normalize("NFC", text).lower().strip()

    for k, v in TONE_MARK_MAP.items():
        text = text.replace(k, v)

    text = re.sub(r"\s+", " ", text)
    return text
