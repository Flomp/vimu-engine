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
        open_color = node.data.get('open_color')
        hidden_color = node.data.get('hidden_color')

        open = node.data.get('open', False)
        hidden = node.data.get('hidden', False)

        if in_0 is not None:
            if open:
                checker.checkConsecutivePossibilities(in_0, checker.parallelFifths, color=open_color)
                checker.checkConsecutivePossibilities(in_0, checker.parallelOctaves, color=open_color)
            if hidden:
                checker.checkConsecutivePossibilities(in_0, checker.hiddenFifth, color=hidden_color)
                checker.checkConsecutivePossibilities(in_0, checker.hiddenOctave, color=hidden_color)

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
