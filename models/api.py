from typing import Any

from pydantic import BaseModel
from pydantic.dataclasses import dataclass


class APIResponse(BaseModel):
    status: str
    data: Any | None
    error: Any | None
