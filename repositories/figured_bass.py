from music21.figuredBass import realizer

from models.engine import EngineNode, WorkerInputs, WorkerOutputs
from repositories.repository import Repository


class FiguredBassRealizeRepository(Repository):
    def process(self, node: EngineNode, input_data: WorkerInputs, output_data: WorkerOutputs):
        in_0 = input_data.get('in_0')

        if in_0 is not None:
            s = realizer.figuredBassFromStream(in_0)
            r = s.realize()
            r.generateRealizationFromPossibilityProgression()
