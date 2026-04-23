from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..managers import DatabaseServiceManager

from base import QObjectBase

from .models import Sentence


class SentenceService(QObjectBase):

    def __init__(self, db_service: DatabaseServiceManager):
        super().__init__()
        self.db_service = db_service

    def remove_duplicates(self, sentences: list[Sentence]):
        result = self.db_service.read.sentences.exists(sentences)
        self.logging(f"Found {len(result)} sentences that already exist in the db.")
        unique_sentences = [
            sentence for sentence in sentences if sentence.chinese not in result
        ]
        return unique_sentences
