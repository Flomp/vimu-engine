from typing import Any

from pydantic.dataclasses import dataclass


@dataclass
class APIResponse:
    status: str
    data: Any | None
    error: Any | None
