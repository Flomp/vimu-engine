from enum import Enum
from typing import List

from pydantic import BaseModel

from models.engine import EngineNode


class SocketType(str, Enum):
    int = "int"
    float = "float"
    string = "string"
    bool = "bool"
    list = "list"
    set = "set"
    dict = "dict"
    stream = "stream"
    part = "part"
    object = "object"
    score = "score"


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
