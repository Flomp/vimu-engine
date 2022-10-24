from models.engine import EngineNode, WorkerInputs, WorkerOutputs
from repositories.repository import Repository


class TransformChordifyRepository(Repository):

    def process(self, node: EngineNode, input_data: WorkerInputs, output_data: WorkerOutputs):
        in_0 = input_data.get('in_0')

        if in_0 is not None:
            output = in_0.chordify()
            for c in output.recurse().getElementsByClass('Chord'):
                c.closedPosition(forceOctave=4, inPlace=True)

            for key in node.outputs.keys():
                output_data[key] = output


class TransformTransposeRepository(Repository):

    def process(self, node: EngineNode, input_data: WorkerInputs, output_data: WorkerOutputs):
        in_0 = input_data.get('in_0')
        steps = node.data.get('data')
        if in_0 is not None and steps is not None:
            output = in_0.transpose(int(steps))

            for key in node.outputs.keys():
                output_data[key] = output


class TransformFlattenRepository(Repository):

    def process(self, node: EngineNode, input_data: WorkerInputs, output_data: WorkerOutputs):
        in_0 = input_data.get('in_0')
        if in_0 is not None:
            output = in_0.flatten()

            for key in node.outputs.keys():
                output_data[key] = output
