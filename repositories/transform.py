from music21 import stream

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


class TransformStackRepository(Repository):

    def process(self, node: EngineNode, input_data: WorkerInputs, output_data: WorkerOutputs):
        in_0 = input_data.get('in_0')
        in_1 = input_data.get('in_1')
        if in_0 is not None and in_1 is not None:
            output = stream.Stream()
            if in_0.hasPartLikeStreams():
                for part in in_0.parts:
                    output.insert(0, part)
            else:
                output.insert(in_0)

            if in_1.hasPartLikeStreams():
                for part in in_1.parts:
                    output.insert(0, part)
            else:
                output.insert(0, in_1)

            for key in node.outputs.keys():
                output_data[key] = output


class TransformAppendRepository(Repository):

    def process(self, node: EngineNode, input_data: WorkerInputs, output_data: WorkerOutputs):
        in_0 = input_data.get('in_0')
        in_1 = input_data.get('in_1')
        match_instruments = node.data.get('match_instruments')

        if in_0 is not None and in_1 is not None:
            in0_parts = [in_0] if isinstance(in_0, stream.Part) else in_0.recurse().parts
            in1_parts = [in_1] if isinstance(in_1, stream.Part) else in_1.recurse().parts
            for i, p in enumerate(in0_parts):
                if match_instruments:
                    parts_with_same_id = list(filter(lambda op: op.id == p.id, in1_parts))

                    if len(parts_with_same_id) == 0:
                        continue

                    other_part = parts_with_same_id[0]
                else:
                    if i >= len(in1_parts):
                        break
                    other_part = in1_parts[i]

                for m in other_part.recurse().getElementsByClass(stream.Measure):
                    p.append(m)

            for key in node.outputs.keys():
                output_data[key] = in_0
