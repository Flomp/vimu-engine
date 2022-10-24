from music21 import corpus, stream, converter, roman, key as m21Key, note, interval, search


class SourceRepository:
    def corpus(self, work_name: str):
        return corpus.parse(work_name)

    def tinynotation(self, tinynotation: str):
        return converter.parse('tinynotation:' + tinynotation)


class SelectRepository:
    def part(self, data: stream.Score, part: int):
        return data.parts[part]

    def measures(self, data: stream.Stream, start: int, end: int):
        return data.measures(start, end)

    def notes(self, data: stream.Stream, start: int, end: int):
        s = stream.Stream()
        s.append(data.flat.notes[start:end])
        return s


class TransformRepository:
    def chordify(self, data: stream.Stream):
        s = data.chordify()
        for c in s.recurse().getElementsByClass('Chord'):
            c.closedPosition(forceOctave=4, inPlace=True)
        return s

    def transpose(self, data: stream.Stream, steps: int):
        return data.transpose(steps)

    def flatten(self, data: stream.Stream):
        return data.flatten()


class AnalysisRepository:
    def key(self, data: stream.Stream):
        return data.analyze('key')

    def ambitus(self, data: stream.Stream) -> interval.Interval:
        return data.analyze('ambitus')

    def romanNumeral(self, data: stream.Stream, key: m21Key.Key):
        chords = data.chordify()
        if type(data) is stream.Score:
            last_part = data.parts[-1]
        else:
            last_part = data

        for c in chords.flatten().getElementsByClass('Chord'):
            rn = roman.romanNumeralFromChord(c, key)
            for n in last_part.flatten().getElementsByOffset(c.offset):
                try:
                    n.addLyric(str(rn.figure))
                except:
                    continue

        return data


class SearchRepository:
    def part(self, data: stream.Stream, part: stream.Stream, color: str = "red"):
        notes = data.recurse().notes
        search_list = list(part.recurse().notes)
        matches = search.noteNameRhythmicSearch(notes, search_list)
        for m in matches:
            for i in range(m, m+len(search_list)):
                matched_note = notes[i]
                matched_note.style.color = color
        return data

    def lyrics(self, data: stream.Stream, lyrics: str, color: str = "red"):
        ls = search.lyrics.LyricSearcher(data)
        matches = ls.search(lyrics)
        for m in matches:
            for el in m.els:
                el.style.color = color
        return data
