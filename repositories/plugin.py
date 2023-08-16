import asyncio
import threading

from models.engine import EngineNode, WorkerInputs, WorkerOutputs
from repositories.repository import Repository


class PluginRepository(Repository):
    def process(self, node: EngineNode, input_data: WorkerInputs, output_data: WorkerOutputs):
        code = node.data.get('code', '')

        thread = threading.Thread(target=run_code, args=(code, node, input_data, output_data))
        thread.start()
        thread.join(timeout=10)

        if thread.is_alive():
            raise asyncio.TimeoutError("Execution timed out")


def run_code(code, node, input_data, output_data):
    exec(code,
         {'input_data': input_data, 'node': node, 'output_data': output_data})
