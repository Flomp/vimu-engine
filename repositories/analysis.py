from music21 import stream, key as m21_key, roman, interval, note

from models.engine import EngineNode, WorkerInputs, WorkerOutputs
from repositories.repository import Repository


class AnalysisKeyRepository(Repository):

    def process(self, node: EngineNode, input_data: WorkerInputs, output_data: WorkerOutputs):
        in_0: stream = input_data.get('in_0')

        if in_0 is not None:
            output = in_0.analyze('key')
            for key in node.outputs.keys():
                output_data[key] = output


class AnalysisAmbitusRepository(Repository):

    def process(self, node: EngineNode, input_data: WorkerInputs, output_data: WorkerOutputs):
        in_0: stream = input_data.get('in_0')

        if in_0 is not None:
            output = stream.Score()
            itv: interval.Interval = in_0.analyze('ambitus')
            lower_note = note.Note(itv.pitchStart)
            upper_note = note.Note(itv.pitchEnd)

            lower_note.insertLyric(lower_note.nameWithOctave)
            upper_note.insertLyric(upper_note.nameWithOctave)
            output.append(lower_note)
            output.append(upper_note)
            for key in node.outputs.keys():
                output_data[key] = output


class AnalysisRomanNumeralRepository(Repository):

    def process(self, node: EngineNode, input_data: WorkerInputs, output_data: WorkerOutputs):
        in_0: m21_key = input_data.get('in_0')
        in_1: stream = input_data.get('in_1')

        if in_0 is not None and in_1 is not None:
            output = in_1.chordify()
            if type(in_1) is stream.Score:
                last_part = in_1.parts[-1]
            else:
                last_part = in_1

            for c in output.flatten().getElementsByClass('Chord'):
                rn = roman.romanNumeralFromChord(c, in_0)
                for n in last_part.flatten().getElementsByOffset(c.offset):
                    try:
                        n.addLyric(str(rn.figure))
                    except:
                        continue
            for key in node.outputs.keys():
                output_data[key] = in_1
