from music21 import converter
from music21.figuredBass import realizer, examples, rules

from models.engine import EngineNode, WorkerInputs, WorkerOutputs
from repositories.repository import Repository


class FiguredBassRealizeRepository(Repository):
    def process(self, node: EngineNode, input_data: WorkerInputs, output_data: WorkerOutputs):
        in_0 = input_data.get('in_0')

        if in_0 is not None:
            s = realizer.figuredBassFromStream(in_0)
            fb_rules = rules.Rules()
            fb_rules.partMovementLimits = [(1, 2), (2, 5), (3, 5)]
            r = s.realize(fb_rules)
            output = r.generateRandomRealization()

            for key in node.outputs.keys():
                output_data[key] = output
