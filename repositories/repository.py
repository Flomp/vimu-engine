from abc import ABC, abstractmethod

from models.engine import EngineNode, WorkerInputs, WorkerOutputs


class Repository(ABC):
    @abstractmethod
    def process(self, node: EngineNode, input_data: WorkerInputs, output_data: WorkerOutputs):
        pass
