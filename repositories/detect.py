import pickle

import numpy as np
from music21 import analysis, corpus, stream
from music21.figuredBass import checker

from models.engine import EngineNode, WorkerInputs, WorkerOutputs
from repositories.repository import Repository


class DetectModulationRepository(Repository):
    KEYS = (
        'C', 'Db', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B',
        'c', 'c#', 'd', 'eb', 'e', 'f', 'f#', 'g', 'ab', 'a', 'bb', 'b',
    )

    @staticmethod
    def stream_2_pitch_vector(s: stream):
        ks_analyzer = analysis.discrete.KrumhanslSchmuckler()
        wa = analysis.windowed.WindowedAnalysis(s, ks_analyzer)
        c = wa.getMinimumWindowStream()
        slices = []
        for ev in c.flat.notes:
            slices.append(ev.pitch.pitchClass)

        return np.array(slices).reshape(1, -1), c

    def process(self, node: EngineNode, input_data: WorkerInputs, output_data: WorkerOutputs):
        in_0 = input_data.get('in_0')

        if in_0 is not None:
            with open("bin/hmm.pickle", "rb") as file:
                model = pickle.load(file)

            v, c = self.stream_2_pitch_vector(in_0)
            pred = model.predict(v)

            idx = 0
            last_part = in_0.parts[-1].flatten()
            previous_key = ""
            for i, m in enumerate(c.getElementsByClass('Measure')):
                window_size = len(m.notes)
                pred_window = pred[idx:idx + window_size]
                if len(pred_window) == 0:
                    continue
                values, counts = np.unique(pred_window, return_counts=True)
                ind = np.argmax(counts)
                most_common_key = self.KEYS[values[ind]]
                if previous_key != most_common_key:
                    text = f'{previous_key}→{most_common_key}'
                    previous_key = most_common_key
                    el = last_part.notesAndRests.getElementsByOffset(i)
                    try:
                        el[0].lyric = text
                    except:
                        print("here")
                        continue

                idx += window_size

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
