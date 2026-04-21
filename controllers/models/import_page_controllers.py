from dataclasses import dataclass

from ..lessons_controller import LessonsController


@dataclass
class ImportPageControllers:
    lessons: LessonsController
