from pydantic.dataclasses import dataclass
from typing import Dict, Any, List, Annotated


@dataclass
class ConnectionData:
    node: int
    data: Any


@dataclass
class InputConnectionData(ConnectionData):
    output: str


@dataclass
class OutputConnectionData(ConnectionData):
    input: str


@dataclass
class InputsData:
    connections: list[InputConnectionData]


@dataclass
class OutputsData:
    connections: list[OutputConnectionData]


@dataclass
class WorkerInputs(Dict[str, list]):
    pass


@dataclass
class WorkerOutputs(Dict[str, Any]):
    pass


@dataclass
class NodeData:
    id: int
    name: str
    inputs: Dict[str, InputsData]
    outputs: Dict[str, OutputsData]
    data: Dict[str, Any]
    position: Annotated[List[float], 2]


@dataclass
class NodesData:
    id: NodeData


@dataclass
class EngineNode(NodeData):
    outputData: WorkerOutputs | None = None


@dataclass
class Data:
    id: str
    nodes: Dict[int, EngineNode]
