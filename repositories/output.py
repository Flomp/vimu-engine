from models.engine import EngineNode, WorkerInputs, WorkerOutputs
from repositories.repository import Repository


class OutputRepository(Repository):
    def process(self, node: EngineNode, input_data: WorkerInputs, output_data: WorkerOutputs):
        in_0 = input_data.get('in_0')
        if in_0 is not None:
            node.data['output'] = open(in_0.write()).read()
