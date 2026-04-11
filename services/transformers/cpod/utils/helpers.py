from base.enums import LESSONLEVEL


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
