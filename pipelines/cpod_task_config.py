from base.enums import EXTRACTDATASOURCE, FAILURESTRATEGY, LESSONTASK
from models.pipelines import TaskCapability, TaskPolicy
from models.pipelines.task_definition import TaskDefinition

TASK_GRAPH: dict[LESSONTASK, TaskDefinition] = {
    LESSONTASK.INFO: TaskDefinition(
        next_tasks=[
            LESSONTASK.LESSON_AUDIO,
            LESSONTASK.DIALOGUE,
        ],
        sources=[EXTRACTDATASOURCE.SCRAPE],
        policy=TaskPolicy(
            max_retries=2,
            retry_delay_ms=5000,
            backoff=True,
            partial_threshold=None,
            failure_strategy=FAILURESTRATEGY.RETRY,
            is_criticial=True,
        ),
        capability=TaskCapability(
            transform=True,
            process=True,
        ),
    ),
    LESSONTASK.DIALOGUE: TaskDefinition(
        next_tasks=[LESSONTASK.VOCAB],
        sources=[EXTRACTDATASOURCE.API, EXTRACTDATASOURCE.SCRAPE],
        policy=TaskPolicy(
            max_retries=2,
            retry_delay_ms=5000,
            backoff=True,
            partial_threshold=None,
            failure_strategy=FAILURESTRATEGY.FALLBACK,
            is_criticial=False,
        ),
        capability=TaskCapability(
            transform=True,
            process=True,
        ),
    ),
    LESSONTASK.VOCAB: TaskDefinition(
        next_tasks=[LESSONTASK.EXPANSION],
        sources=[EXTRACTDATASOURCE.API, EXTRACTDATASOURCE.SCRAPE],
        policy=TaskPolicy(
            max_retries=2,
            retry_delay_ms=5000,
            backoff=True,
            partial_threshold=None,
            failure_strategy=FAILURESTRATEGY.FALLBACK,
            is_criticial=False,
        ),
        capability=TaskCapability(
            transform=True,
            process=True,
        ),
    ),
    LESSONTASK.EXPANSION: TaskDefinition(
        next_tasks=[LESSONTASK.GRAMMAR],
        sources=[EXTRACTDATASOURCE.API, EXTRACTDATASOURCE.SCRAPE],
        policy=TaskPolicy(
            max_retries=2,
            retry_delay_ms=5000,
            backoff=True,
            partial_threshold=None,
            failure_strategy=FAILURESTRATEGY.FALLBACK,
            is_criticial=False,
        ),
        capability=TaskCapability(
            transform=True,
            process=True,
        ),
    ),
    LESSONTASK.GRAMMAR: TaskDefinition(
        next_tasks=[LESSONTASK.CHECK],
        sources=[EXTRACTDATASOURCE.API, EXTRACTDATASOURCE.SCRAPE],
        policy=TaskPolicy(
            max_retries=2,
            retry_delay_ms=5000,
            backoff=True,
            partial_threshold=None,
            failure_strategy=FAILURESTRATEGY.FALLBACK,
            is_criticial=False,
        ),
        capability=TaskCapability(
            transform=True,
            process=True,
        ),
    ),
    LESSONTASK.CHECK: TaskDefinition(
        next_tasks=[LESSONTASK.SAVE_LESSON, LESSONTASK.AUDIO],
        sources=[EXTRACTDATASOURCE.SCRAPE],
        policy=TaskPolicy(
            max_retries=2,
            retry_delay_ms=5000,
            backoff=True,
            partial_threshold=None,
            failure_strategy=FAILURESTRATEGY.RETRY,
            is_criticial=False,
        ),
        capability=TaskCapability(
            transform=False,
            process=True,
        ),
    ),
    LESSONTASK.LESSON_AUDIO: TaskDefinition(
        next_tasks=[LESSONTASK.TRANSCRIBE],
        sources=[],
        policy=TaskPolicy(
            max_retries=2,
            retry_delay_ms=5000,
            backoff=True,
            partial_threshold=None,
            failure_strategy=FAILURESTRATEGY.RETRY,
            is_criticial=False,
        ),
        capability=TaskCapability(
            transform=False,
            process=False,
        ),
    ),
    LESSONTASK.AUDIO: TaskDefinition(
        next_tasks=[LESSONTASK.COMBINE_AUDIO],
        sources=[],
        policy=TaskPolicy(
            max_retries=2,
            retry_delay_ms=5000,
            backoff=True,
            partial_threshold=90,
            failure_strategy=FAILURESTRATEGY.RETRY,
            is_criticial=False,
        ),
        capability=TaskCapability(
            transform=False,
            process=False,
        ),
    ),
    LESSONTASK.SAVE_LESSON: TaskDefinition(
        next_tasks=[],
        sources=[],
        policy=TaskPolicy(
            max_retries=2,
            retry_delay_ms=5000,
            backoff=True,
            partial_threshold=None,
            failure_strategy=FAILURESTRATEGY.RETRY,
            is_criticial=False,
        ),
        capability=TaskCapability(
            transform=False,
            process=False,
        ),
    ),
    LESSONTASK.TRANSCRIBE: TaskDefinition(
        next_tasks=[LESSONTASK.LINGQ_LESSON],
        sources=[],
        policy=TaskPolicy(
            max_retries=2,
            retry_delay_ms=5000,
            backoff=True,
            partial_threshold=None,
            failure_strategy=FAILURESTRATEGY.RETRY,
            is_criticial=False,
        ),
        capability=TaskCapability(
            transform=False,
            process=False,
        ),
    ),
    LESSONTASK.COMBINE_AUDIO: TaskDefinition(
        next_tasks=[
            LESSONTASK.LINGQ_SENTS,
            LESSONTASK.LINGQ_DIALOGUE,
        ],
        sources=[],
        policy=TaskPolicy(
            max_retries=2,
            retry_delay_ms=5000,
            backoff=True,
            partial_threshold=None,
            failure_strategy=FAILURESTRATEGY.RETRY,
            is_criticial=False,
        ),
        capability=TaskCapability(
            transform=False,
            process=False,
        ),
    ),
    LESSONTASK.LINGQ_LESSON: TaskDefinition(
        next_tasks=[],
        sources=[],
        policy=TaskPolicy(
            max_retries=2,
            retry_delay_ms=5000,
            backoff=True,
            partial_threshold=None,
            failure_strategy=FAILURESTRATEGY.RETRY,
            is_criticial=False,
        ),
        capability=TaskCapability(
            transform=False,
            process=False,
        ),
    ),
    LESSONTASK.LINGQ_SENTS: TaskDefinition(
        next_tasks=[],
        sources=[],
        policy=TaskPolicy(
            max_retries=2,
            retry_delay_ms=5000,
            backoff=True,
            partial_threshold=None,
            failure_strategy=FAILURESTRATEGY.RETRY,
            is_criticial=False,
        ),
        capability=TaskCapability(
            transform=False,
            process=False,
        ),
    ),
    LESSONTASK.LINGQ_DIALOGUE: TaskDefinition(
        next_tasks=[],
        sources=[],
        policy=TaskPolicy(
            max_retries=2,
            retry_delay_ms=5000,
            backoff=True,
            partial_threshold=None,
            failure_strategy=FAILURESTRATEGY.RETRY,
            is_criticial=False,
        ),
        capability=TaskCapability(
            transform=False,
            process=False,
        ),
    ),
}
