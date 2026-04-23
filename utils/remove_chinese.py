import re


def remove_chinese(text: str) -> str:
    return re.sub(r"[\u4E00-\u9FFF]+", "", text)
