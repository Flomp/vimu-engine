from enum import Enum
from typing import List

from pydantic import BaseModel

from models.engine import EngineNode


class SocketType(str, Enum):
    stream = "stream"
    part = "part"
    object = "object"
    score = "score"
    number = "number"


class PluginSocket(BaseModel):
    key: str
    name: str
    type: SocketType


class PluginConfig(BaseModel):
    inputs: List[PluginSocket]
    outputs: List[PluginSocket]

class Plugin(BaseModel):
    code: str
    config: PluginConfig

class TestPluginRequest(BaseModel):
    plugin: Plugin
    node: EngineNode
