import json

import music21.corpus.chorales
import requests

from musicxml_engine import MusicXMLEngine

mxml = MusicXMLEngine()

#@request.auth.id != "" && score.owner = @request.auth.id
def seed():
    for s in music21.corpus.chorales.Iterator():
        raw = open(s.write(), "rb").read()
        meta = mxml.meta(raw)
        thumbnail = mxml.thumbnail(raw)

        files = {
            'data': raw,
            'thumbnail': thumbnail
        }
        data = {
            'name': s.metadata.bestTitle,
            'public': True
        }
        response = requests.post('https://pb.vimu.app/api/collections/scores/records',
                                 files=files, data=data)

        score = json.loads(response.text)

        meta['score'] = score['id']

        response = requests.post('https://pb.vimu.app/api/collections/score_meta/records',
                                 json=meta)

        print(s.metadata.bestTitle)


if __name__ == '__main__':
    seed()