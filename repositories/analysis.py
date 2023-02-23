import music21.key
from music21 import stream, roman, interval, note

from models.engine import EngineNode, WorkerInputs, WorkerOutputs
from repositories.AugmentedNet.inference import augmented_net
from repositories.repository import Repository


class AnalysisKeyRepository(Repository):

    def process(self, node: EngineNode, input_data: WorkerInputs, output_data: WorkerOutputs):
        in_0: stream = input_data.get('in_0')

        if in_0 is not None:
            in_key: music21.key.Key = in_0.analyze('key')
            output = music21.musicxml.m21ToXml.GeneralObjectExporter().fromScale(in_key)

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
        in_1: stream = input_data.get('in_1')
        key = node.data.get('data')

        if in_1 is not None:
            if key:
                output = in_1.chordify()
                if type(in_1) is stream.Score:
                    last_part = in_1.parts[-1]
                else:
                    last_part = in_1

                for c in output.flatten().getElementsByClass('Chord'):
                    rn = roman.romanNumeralFromChord(c, key)
                    for n in last_part.flatten().getElementsByOffset(c.offset):
                        try:
                            n.addLyric(str(rn.figure))
                        except:
                            continue
            else:
                in_1 = augmented_net.predict(in_1)

            for key in node.outputs.keys():
                output_data[key] = in_1
