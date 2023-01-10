from models.engine import Data, EngineNode, InputConnectionData, WorkerOutputs, WorkerInputs
from repositories.analysis import AnalysisKeyRepository, AnalysisRomanNumeralRepository, AnalysisAmbitusRepository
from repositories.detect import DetectModulationRepository, DetectParallelsRepository, DetectVoiceCrossingsRepository
from repositories.figured_bass import FiguredBassRealizeRepository
from repositories.output import OutputRepository
from repositories.plot import PlotHistogramRepository, PlotBarRepository, PlotScatterRepository, \
    PlotScatterWeightedRepository, PlotBarWeightedRepository
from repositories.search import SearchPartRepository, SearchLyricsRepository
from repositories.select import SelectMeasuresRepository, SelectPartsRepository, SelectNotesRepository
from repositories.source import SourceCorpusRepository, SourceTinynotationRepository, SourceScoreRepository
from repositories.transform import TransformTransposeRepository, TransformChordifyRepository, TransformFlattenRepository


def get_repo(node_name: str):
    if node_name == "output":
        return OutputRepository()
    elif node_name == "source_score":
        return SourceScoreRepository()
    elif node_name == "source_corpus":
        return SourceCorpusRepository()
    elif node_name == "source_tinynotation":
        return SourceTinynotationRepository()
    elif node_name == "select_measures":
        return SelectMeasuresRepository()
    elif node_name == "select_parts":
        return SelectPartsRepository()
    elif node_name == "select_notes":
        return SelectNotesRepository()
    elif node_name == "transform_transpose":
        return TransformTransposeRepository()
    elif node_name == "transform_chordify":
        return TransformChordifyRepository()
    elif node_name == "transform_flatten":
        return TransformFlattenRepository()
    elif node_name == "analysis_key":
        return AnalysisKeyRepository()
    elif node_name == "analysis_ambitus":
        return AnalysisAmbitusRepository()
    elif node_name == "analysis_roman_numeral":
        return AnalysisRomanNumeralRepository()
    elif node_name == "search_part":
        return SearchPartRepository()
    elif node_name == "search_lyrics":
        return SearchLyricsRepository()
    elif node_name == "figured_bass_realize":
        return FiguredBassRealizeRepository()
    elif node_name == "detect_modulation":
        return DetectModulationRepository()
    elif node_name == "detect_parallels":
        return DetectParallelsRepository()
    elif node_name == "detect_voice_crossings":
        return DetectVoiceCrossingsRepository()
    elif node_name == "plot_histogram":
        return PlotHistogramRepository()
    elif node_name == "plot_piano_roll":
        return PlotBarRepository()
    elif node_name == "plot_dynamics":
        return PlotBarWeightedRepository()
    elif node_name == "plot_scatter":
        return PlotScatterRepository()
    elif node_name == "plot_scatter_weighted":
        return PlotScatterWeightedRepository()
    return None


class EngineException(Exception):
    def __init__(self, message, node: EngineNode):
        super().__init__(message)

        self.node = node


class Engine:
    data: Data
    forwarded = set()
    plots = set()

    def process(self, data: Data):
        self.data = data
        self.forwarded.clear()
        self.plots.clear()

        self.process_start_node()
        self.process_unreachable()

        output_node = self.find_output_node()

        if output_node is None:
            raise Exception('No output node found!')

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
            self.plots.add(node.outputData['plot'])

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
