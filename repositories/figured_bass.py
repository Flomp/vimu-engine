from music21.figuredBass import realizer, rules

from models.engine import EngineNode, WorkerInputs, WorkerOutputs
from repositories.repository import Repository


class FiguredBassRealizeRepository(Repository):
    def process(self, node: EngineNode, input_data: WorkerInputs, output_data: WorkerOutputs):
        in_0 = input_data.get('in_0')
        keyboard_output = node.data.get('keyboard_output')
        incomplete_chords = node.data.get('incomplete_chords')
        semi_tones = node.data.get('semi_tones')

        if in_0 is not None:
            s = realizer.figuredBassFromStream(in_0.flat)
            fb_rules = rules.Rules()
            fb_rules.partMovementLimits = [(1, 2), (2, 12), (3, 12)]
            fb_rules.forbidIncompletePossibilities = not incomplete_chords
            fb_rules.upperPartsMaxSemitoneSeparation = int(semi_tones) if semi_tones != '' else None
            r = s.realize(fb_rules)
            r.keyboardStyleOutput = keyboard_output
            output = r.generateRandomRealization()

            for key in node.outputs.keys():
                output_data[key] = output
