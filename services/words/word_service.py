from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..managers import DatabaseServiceManager

from base import QObjectBase

from .models import Word


class WordService(QObjectBase):

    def __init__(self, db_service: DatabaseServiceManager):
        super().__init__()
        self.db_service = db_service

    def remove_duplicates(self, words: list[Word]):
        result = self.db_service.read.words.exists(words)
        self.logging(f"Found {len(result)} words that already exist in the db.")
        unique_words = [word for word in words if word.chinese not in result]
        return unique_words
