import os

import requests
from music21 import corpus, converter

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
            POCKETBASE_URL = os.getenv("POCKET_BASEURL", "https://vimu-pocketbase-production.up.railway.app")
            url = f'{POCKETBASE_URL}/api/files/scores/{score.get("id")}/{score.get("data")}'
            response = requests.get(url)
            if response.ok:
                output = converter.parse(response.text)
                for key in node.outputs.keys():
                    output_data[key] = output


class SourceTinynotationRepository(Repository):
    def process(self, node: EngineNode, input_data: WorkerInputs, output_data: WorkerOutputs):
        tinynotation = node.data.get('data')
        if tinynotation is not None:
            data = converter.parse('tinynotation:' + tinynotation)
            for key in node.outputs.keys():
                output_data[key] = data
