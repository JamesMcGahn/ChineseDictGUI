from dataclasses import dataclass


@dataclass(frozen=True)
class TaskPolicy:
    max_retries: int = 0
    retry_delay_ms: int = 2_000
    backoff: bool = True
    partial_threshold: int | None = None
