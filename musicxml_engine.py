import music21
from music21 import converter
import verovio


class MusicXMLEngine:
    s: music21.stream

    def __init__(self):
        self.ld = music21.text.LanguageDetector()
        self.tk = verovio.toolkit()
        self.tk.setOption('pageHeight', '1000')

    def thumbnail(self, raw: bytes):
        self.tk.loadData(raw.decode('utf-8'))
        svg_file = self.tk.renderToSVG()
        return svg_file.encode('utf-8')

    def meta(self, raw: bytes):
        s = converter.parse(raw)
        if s is None:
            return {}
        instruments = " ".join([(part.partName if part.partName is not None else "") for part in s.recurse().parts])
        keys = " ".join(
            {getattr(key, "tonicPitchNameWithCase", "") for key in s.recurse().getElementsByClass('KeySignature')})
        language = self.ld.mostLikelyLanguage(music21.text.assembleLyrics(s))
        times = " ".join({time.ratioString for time in s.recurse().getElementsByClass('TimeSignature')})
        return {
            "composer": s.metadata.composer,
            "date": s.metadata.date,
            "instruments": instruments,
            "keys": keys,
            "language": language,
            "times": times,
            "lyrics": music21.text.assembleLyrics(s)
        }
