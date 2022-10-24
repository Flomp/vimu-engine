from music21 import stream

from models.engine import EngineNode, WorkerInputs, WorkerOutputs
from repositories.repository import Repository


class SelectPartRepository(Repository):

    def process(self, node: EngineNode, input_data: WorkerInputs, output_data: WorkerOutputs):
        in_0 = input_data.get('in_0')
        part = int(node.data.get('data'))

        if in_0 is not None and part is not None:
            output = in_0.parts[part]
            for key in node.outputs.keys():
                output_data[key] = output


class SelectMeasuresRepository(Repository):

    def process(self, node: EngineNode, input_data: WorkerInputs, output_data: WorkerOutputs):
        in_0 = input_data.get('in_0')
        measures = node.data.get('data')

        if in_0 is not None and measures is not None:
            output = in_0.measures(int(measures[0]), int(measures[1]))
            for key in node.outputs.keys():
                output_data[key] = output


class SelectNotesRepository(Repository):

    def process(self, node: EngineNode, input_data: WorkerInputs, output_data: WorkerOutputs):
        in_0 = input_data.get('in_0')
        notes = node.data.get('data')

        if in_0 is not None and notes is not None:
            output = stream.Stream()
            output.append(in_0.flat.notes[notes[0]:notes[1]])
            for key in node.outputs.keys():
                output_data[key] = output
