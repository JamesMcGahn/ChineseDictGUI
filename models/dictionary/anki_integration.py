from dataclasses import dataclass


@dataclass
class AnkiIntegration:
    anki_update: int = 0
    local_update: int = 0
    id: int = 1
    initial_import_done: int = 0
