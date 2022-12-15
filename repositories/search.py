from music21 import search as m21_search, chord

from models.engine import EngineNode, WorkerInputs, WorkerOutputs
from repositories.repository import Repository


class SearchPartRepository(Repository):
    def common_search_algorithm(self, stream_el, search_el, rhythm: bool = True):
        if type(search_el) != type(stream_el):
            return False
        if type(search_el) == chord.Chord:
            if len(search_el.notes) != len(stream_el.notes):
                return False
            return all([self.common_search_algorithm(search_el.notes[i], stream_el.notes[i], rhythm) for i in
                        range(len(search_el.notes))])

        if 'Wildcard' in search_el.classes:
            return True
        if not hasattr(search_el, 'name'):
            return False
        if not hasattr(stream_el, 'name'):
            return False

        if search_el.name != stream_el.name:
            return False

        if 'WildcardDuration' in search_el.duration.classes:
            return True
        if search_el.duration.quarterLength != stream_el.duration.quarterLength and rhythm:
            return False

        return True

    def pitch_rhythm_algorithm(self, stream_el, search_el):
        return self.common_search_algorithm(stream_el, search_el, rhythm=True)

    def pitch_algorithm(self, stream_el, search_el):
        return self.common_search_algorithm(stream_el, search_el, rhythm=False)

    def process(self, node: EngineNode, input_data: WorkerInputs, output_data: WorkerOutputs):
        in_0 = input_data.get('in_0')
        in_1 = input_data.get('in_1')

        color = node.data.get('color')
        pitch = node.data.get('pitch')
        rhythm = node.data.get('rhythm')

        if None not in (in_0, in_1, color):
            notes = in_1.recurse().notes
            search_list = list(in_0.recurse().notes)
            matches = []
            if pitch and rhythm:
                matches = m21_search.streamSearchBase(notes, search_list, self.pitch_rhythm_algorithm)
            elif pitch and not rhythm:
                matches = m21_search.streamSearchBase(notes, search_list, self.pitch_algorithm)
            elif not pitch and rhythm:
                matches = m21_search.rhythmicSearch(notes, search_list)
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

        if None not in (in_0, color):
            if lyrics is not None:
                ls = m21_search.lyrics.LyricSearcher(in_0)
                matches = ls.search(lyrics)
                for m in matches:
                    for el in m.els:
                        el.style.color = color
            for key in node.outputs.keys():
                output_data[key] = in_0
