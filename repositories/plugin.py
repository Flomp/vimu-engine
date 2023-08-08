from models.engine import EngineNode, WorkerInputs, WorkerOutputs
from repositories.repository import Repository


class PluginRepository(Repository):
    def process(self, node: EngineNode, input_data: WorkerInputs, output_data: WorkerOutputs):
        code = node.data.get('code', '')
        loc = {}

        exec(code,
             {'input_data': input_data, 'node': node, 'output_data': output_data}, loc)
