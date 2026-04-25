from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import Word

from base import QObjectBase
from utils.normalize_pinyin import normalize_pinyin


class WordRegistry(QObjectBase):

    def __init__(self):
        super().__init__()
        self._items: dict[str, Word] = {}
        self._by_lookup_key: dict[str, str] = {}
        self._by_chinese: dict[str, set[str]] = {}

    def _lookup_key(self, chinese: str, pinyin: str) -> str:
        return f"{chinese}|{normalize_pinyin(pinyin)}"

    def get(self, runtime_id: str) -> Word | None:
        return self._items.get(runtime_id)

    def find_by_chinese(self, chinese: str) -> list[Word]:
        found_ids = self._by_chinese.get(chinese)
        if not found_ids:
            return []
        return [self._items[id] for id in found_ids if id in self._items]

    def find_exact(self, chinese: str, pinyin: str) -> Word | None:
        text = self._lookup_key(chinese, pinyin)
        runtime_id = self._by_lookup_key.get(text)
        return self._items.get(runtime_id)

    def upsert(self, word: Word) -> None:
        self.remove(word.runtime_id)
        pinyin = normalize_pinyin(word.pinyin)
        text = f"{word.chinese}|{pinyin}"
        self._by_lookup_key[text] = word.runtime_id
        self._by_chinese.setdefault(word.chinese, set())
        self._by_chinese[word.chinese].add(word.runtime_id)
        self._items[word.runtime_id] = word

    def remove(self, runtime_id: str) -> None:
        word = self._items.get(runtime_id)
        if not word:
            return
        text = self._lookup_key(word.chinese, word.pinyin)
        self._by_lookup_key.pop(text, None)
        chinese_set = self._by_chinese.get(word.chinese)
        if chinese_set:
            chinese_set.discard(runtime_id)
            if not chinese_set:
                self._by_chinese.pop(word.chinese, None)
        self._items.pop(runtime_id, None)

    def exists(self, runtime_id: str) -> bool:
        return runtime_id in self._items

    def exists_by_chinese_pinyin(self, chinese: str, pinyin: str) -> bool:
        return self.find_exact(chinese, pinyin) is not None

    def all(self) -> list[Word]:
        return list(self._items.values())

    def clear(self) -> None:
        self._items.clear()
        self._by_lookup_key.clear()
        self._by_chinese.clear()
