from music21.figuredBass import checker

from models.engine import EngineNode, WorkerInputs, WorkerOutputs
from repositories.AugmentedNet.inference import augmented_net
from repositories.repository import Repository


class DetectModulationRepository(Repository):
    def process(self, node: EngineNode, input_data: WorkerInputs, output_data: WorkerOutputs):
        in_0 = input_data.get('in_0')

        if in_0 is not None:
            in_0 = augmented_net.predict(in_0, include_roman_numerals=False)

            for key in node.outputs.keys():
                output_data[key] = in_0


class DetectParallelsRepository(Repository):
    def process(self, node: EngineNode, input_data: WorkerInputs, output_data: WorkerOutputs):
        in_0 = input_data.get('in_0')
        color = node.data.get('color')

        if in_0 is not None:
            checker.checkConsecutivePossibilities(in_0, checker.parallelFifths, color=color)
            checker.checkConsecutivePossibilities(in_0, checker.parallelOctaves, color=color)

        for key in node.outputs.keys():
            output_data[key] = in_0


class DetectVoiceCrossingsRepository(Repository):
    def process(self, node: EngineNode, input_data: WorkerInputs, output_data: WorkerOutputs):
        in_0 = input_data.get('in_0')
        color = node.data.get('color')

        if in_0 is not None:
            checker.checkSinglePossibilities(in_0, checker.voiceCrossing, color=color)

        for key in node.outputs.keys():
            output_data[key] = in_0
