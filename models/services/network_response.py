from dataclasses import dataclass

import requests


@dataclass(frozen=True)
class NetworkResponse:
    ok: bool
    status: int
    data: dict | list | str | None
    message: str
    raw: requests.Response
