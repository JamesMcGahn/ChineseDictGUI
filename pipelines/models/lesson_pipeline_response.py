from dataclasses import dataclass, field

from base.enums import LESSONTASK
from services.lessons.enums import LESSONPROVIDERS


@dataclass(frozen=True)
class LessonPipelineResponse:
    queue_id: str
    provider: LESSONPROVIDERS
    current_task: LESSONTASK | None = None
    errored_tasks: set[LESSONTASK] = field(default_factory=set)
    completed_tasks: set[LESSONTASK] = field(default_factory=set)
    message: str | None = None
