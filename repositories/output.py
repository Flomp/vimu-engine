import music21

from models.engine import EngineNode, WorkerInputs, WorkerOutputs
from repositories.repository import Repository


class OutputRepository(Repository):
    def process(self, node: EngineNode, input_data: WorkerInputs, output_data: WorkerOutputs):
        in_0: music21.stream.Stream = input_data.get('in_0')
        if in_0 is not None:
            if in_0.metadata is None:
                in_0.metadata = music21.metadata.Metadata(title="vimu Fragment", movementName="", composer="vimu")
            node.data['output'] = open(in_0.write()).read()
