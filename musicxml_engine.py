import io
import zipfile

import music21
from music21 import converter
import verovio
from music21.converter import ArchiveManager
from music21.musicxml.archiveTools import uncompressMXL


class MusicXMLEngine:
    s: music21.stream

    def __init__(self):
        self.ld = music21.text.LanguageDetector()
        self.tk = verovio.toolkit()
        self.tk.setOption('adjustPageHeight', 'true')

    def convert(self, raw: bytes):
        possible_zip_archive = io.BytesIO(raw)
        if zipfile.is_zipfile(possible_zip_archive):
            z = zipfile.ZipFile(possible_zip_archive)
            filename = next(filter(lambda f: 'META-INF' not in f, z.namelist()))
            raw = z.read(filename)

        file_format = self._get_file_format(raw)
        if file_format == 'musicxml':
            return raw
        s = converter.parse(raw)

        return open(s.write(), 'rb').read()

    def thumbnail(self, raw: bytes):
        try:
            self.tk.loadData(raw.decode('utf-8'))
            svg_file = self.tk.renderToSVG()
            return svg_file.encode('utf-8')
        except:
            return b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><title>music-note</title><path d="M12 3V13.55C11.41 13.21 10.73 13 10 13C7.79 13 6 14.79 6 17S7.79 21 10 21 14 19.21 14 17V7H18V3H12Z" /></svg>'

    def meta(self, raw: bytes):
        file_format = self._get_file_format(raw)

        # uncompress if necessary
        possible_zip_archive = io.BytesIO(raw)
        if zipfile.is_zipfile(possible_zip_archive):
            file_format = 'archive'
            z = zipfile.ZipFile(possible_zip_archive)
            filename = next(filter(lambda f: 'META-INF' not in f, z.namelist()))
            raw = z.read(filename)

        s = converter.parse(raw)
        if s is None:
            return {}
        instruments = " ".join([(part.partName if part.partName is not None else "") for part in s.recurse().parts])
        keys = " ".join(
            {getattr(key, "tonicPitchNameWithCase", "") for key in s.recurse().getElementsByClass('KeySignature')})
        language = self.ld.mostLikelyLanguage(music21.text.assembleLyrics(s))
        times = " ".join({time.ratioString for time in s.recurse().getElementsByClass('TimeSignature')})
        composer = s.metadata.composer if s.metadata is not None else None
        date = s.metadata.date if s.metadata is not None else None
        return {
            "composer": composer,
            "date": date,
            "instruments": instruments,
            "keys": keys,
            "language": language,
            "times": times,
            "lyrics": music21.text.assembleLyrics(s),
            "format": file_format
        }

    def _get_file_format(self, raw: bytes):
        file_format = 'unknown'
        data_str = raw.lstrip().decode('utf-8', 'ignore')

        if data_str.startswith('<?xml'):
            if '<mei' in data_str:
                file_format = 'mei'
            else:
                file_format = 'musicxml'
        elif data_str.startswith('mei:') or data_str.lower().startswith('mei:'):
            file_format = 'mei'
        elif data_str.lower().startswith('musicxml:'):
            file_format = 'musicxml'
        elif data_str.startswith('MThd') or data_str.lower().startswith('midi:'):
            file_format = 'midi'
        elif (data_str.startswith('!!!')
              or data_str.startswith('**')
              or data_str.lower().startswith('humdrum:')):
            file_format = 'humdrum'
        elif data_str.lower().startswith('tinynotation:'):
            file_format = 'tinyNotation'

        elif 'WK#:' in data_str and 'measure' in data_str:
            file_format = 'musedata'
        elif 'M:' in data_str and 'K:' in data_str:
            file_format = 'abc'
        elif 'Time Signature:' in data_str and 'm1' in data_str:
            file_format = 'romanText'

        return file_format
