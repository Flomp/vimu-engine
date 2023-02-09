from models.engine import Data, EngineNode, InputConnectionData, WorkerOutputs, WorkerInputs
from repositories.analysis import AnalysisKeyRepository, AnalysisRomanNumeralRepository, AnalysisAmbitusRepository
from repositories.detect import DetectModulationRepository, DetectParallelsRepository, DetectVoiceCrossingsRepository
from repositories.figured_bass import FiguredBassRealizeRepository
from repositories.output import OutputRepository
from repositories.plot import PlotHistogramRepository, PlotBarRepository, PlotScatterRepository, \
    PlotScatterWeightedRepository, PlotBarWeightedRepository
from repositories.search import SearchPartRepository, SearchLyricsRepository
from repositories.select import SelectMeasuresRepository, SelectPartsRepository, SelectNotesRepository
from repositories.source import SourceTinynotationRepository, SourceScoreRepository
from repositories.transform import TransformTransposeRepository, TransformChordifyRepository, \
    TransformAppendRepository, TransformStackRepository

repositories = {
    "output": OutputRepository(),
    "source_score": SourceScoreRepository(),
    "source_tinynotation": SourceTinynotationRepository(),
    "select_measures": SelectMeasuresRepository(),
    "select_parts": SelectPartsRepository(),
    "select_notes": SelectNotesRepository(),
    "transform_transpose": TransformTransposeRepository(),
    "transform_chordify": TransformChordifyRepository(),
    "transform_append": TransformAppendRepository(),
    "transform_stack": TransformStackRepository(),
    "analysis_key": AnalysisKeyRepository(),
    "analysis_ambitus": AnalysisAmbitusRepository(),
    "analysis_roman_numeral": AnalysisRomanNumeralRepository(),
    "search_part": SearchPartRepository(),
    "search_lyrics": SearchLyricsRepository(),
    "figured_bass_realize": FiguredBassRealizeRepository(),
    "detect_modulation": DetectModulationRepository(),
    "detect_parallels": DetectParallelsRepository(),
    "detect_voice_crossings": DetectVoiceCrossingsRepository(),
    "plot_histogram": PlotHistogramRepository(),
    "plot_piano_roll": PlotBarRepository(),
    "plot_dynamics": PlotBarWeightedRepository(),
    "plot_scatter": PlotScatterRepository(),
    "plot_scatter_weighted": PlotScatterWeightedRepository(),
}

def get_repo(node_name: str):
    return repositories.get(node_name, None)


class EngineException(Exception):
    def __init__(self, message, node: EngineNode):
        super().__init__(message)

        self.node = node


class Engine:
    data: Data
    forwarded = set()
    plots = list()

    def process(self, data: Data):
        self.data = data
        self.forwarded.clear()
        self.plots.clear()

        output_node = self.find_output_node()

        if output_node is None:
            raise Exception('No output node found!')

        if len(output_node.inputs.get('in_0').connections) > 0:
            self.process_start_node()
            self.process_unreachable()

        return {'output': output_node.data.get('output'), 'plots': self.plots}

    def process_start_node(self, start_id: int = None):

        if start_id is None:
            return

        start_node = self.data.nodes.get(start_id)

        if start_node is None:
            return

        self.process_node(start_node)
        self.forward_process(start_node)

    def process_unreachable(self):
        data = self.data

        for i in self.data.nodes:
            node = data.nodes[i]

            if node.outputData is None:
                self.process_node(node)
                self.forward_process(node)

    def process_node(self, node: EngineNode):
        if node is None:
            return None

        if node.outputData is None:
            node.outputData = self.process_worker(node)

        if 'plot' in node.outputData.keys():
            self.plots.append(node.outputData['plot'])

        return node.outputData

    def forward_process(self, node):
        for key in node.outputs.keys():
            output = node.outputs[key]
            for connection in output.connections:
                next_node = self.data.nodes[connection.node]
                if next_node.id not in self.forwarded:
                    self.forwarded.add(next_node.id)
                    self.process_node(next_node)
                    self.forward_process(next_node)

    def process_worker(self, node):
        input_data = self.extract_input_data(node)
        repo = get_repo(node.name)
        output_data = WorkerOutputs()

        if repo is not None:
            try:
                repo.process(node, input_data, output_data)
            except Exception as e:
                raise EngineException(str(e), node)

        return output_data

    def extract_input_data(self, node: EngineNode):
        obj = WorkerInputs()

        for key in node.inputs.keys():
            node_input = node.inputs[key]
            for connection in node_input.connections:
                prev_node = self.data.nodes[connection.node]
                outputs = self.process_node(prev_node)

                if outputs is not None:
                    obj[key] = outputs.get(connection.output)

        return obj

    def get_connection_data(self, connection: InputConnectionData):
        prev_node = self.data.nodes[connection.node]
        outputs = self.process_node(prev_node)

        return outputs[connection.output]

    def find_output_node(self):
        return next(filter(lambda n: n.name == "output", self.data.nodes.values()), None)
