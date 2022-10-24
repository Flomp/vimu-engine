from music21 import search as m21_search

from models.engine import EngineNode, WorkerInputs, WorkerOutputs
from repositories.repository import Repository


class SearchPartRepository(Repository):

    def process(self, node: EngineNode, input_data: WorkerInputs, output_data: WorkerOutputs):
        in_0 = input_data.get('in_0')
        in_1 = input_data.get('in_1')

        color = node.data.get('color')

        if None not in (in_0, in_1, color):
            notes = in_1.recurse().notes
            search_list = list(in_0.recurse().notes)
            matches = m21_search.noteNameRhythmicSearch(notes, search_list)
            for m in matches:
                for i in range(m, m + len(search_list)):
                    matched_note = notes[i]
                    matched_note.style.color = color

            for key in node.outputs.keys():
                output_data[key] = in_1


class SearchLyricsRepository(Repository):

    def process(self, node: EngineNode, input_data: WorkerInputs, output_data: WorkerOutputs):
        in_0 = input_data.get('in_0')
        lyrics = node.data.get('data')

        color = node.data.get('color')

        if None not in (in_0, lyrics, color):
            ls = m21_search.lyrics.LyricSearcher(in_0)
            matches = ls.search(lyrics)
            for m in matches:
                for el in m.els:
                    el.style.color = color
            for key in node.outputs.keys():
                output_data[key] = in_0
