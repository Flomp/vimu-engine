import os

import music21
import requests
from music21 import corpus, converter, tinyNotation, chord

from config import settings
from models.engine import EngineNode, WorkerInputs, WorkerOutputs
from repositories.repository import Repository


class SourceCorpusRepository(Repository):
    def process(self, node: EngineNode, input_data: WorkerInputs, output_data: WorkerOutputs):
        work_name = node.data.get('data')
        if work_name is not None:
            output = corpus.parse(work_name)
            for key in node.outputs.keys():
                output_data[key] = output


class SourceScoreRepository(Repository):
    def process(self, node: EngineNode, input_data: WorkerInputs, output_data: WorkerOutputs):
        score = node.data.get('data')
        if score is not None:
            POCKETBASE_URL = settings.pocketbase_url
            url = f'{POCKETBASE_URL}/api/files/scores/{score.get("id")}/{score.get("data")}'
            response = requests.get(url)
            if response.ok:
                output = converter.parse(response.text)
                for key in node.outputs.keys():
                    output_data[key] = output


class SourceTinynotationRepository(Repository):

    def process(self, node: EngineNode, input_data: WorkerInputs, output_data: WorkerOutputs):

        class ChordState(tinyNotation.State):
            def affectTokenAfterParse(self, n):
                super(ChordState, self).affectTokenAfterParse(n)
                return None  # do not append Note object

            def end(self):
                ch = chord.Chord(self.affectedTokens)
                ch.duration = self.affectedTokens[0].duration
                return ch

        class KeyToken(tinyNotation.Token):
            def parse(self, parent):
                key_name = self.token
                return music21.key.Key(key_name)

        tinynotation = node.data.get('data')
        if tinynotation is not None:
            tnc = tinyNotation.Converter()
            tnc.load(tinynotation)
            tnc.bracketStateMapping['chord'] = ChordState
            key_mapping = (r'k(.*)', KeyToken)
            tnc.tokenMap.append(key_mapping)

            data = tnc.parse().stream
            for key in node.outputs.keys():
                output_data[key] = data
