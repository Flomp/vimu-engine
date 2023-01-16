import json

import music21.corpus.chorales
import requests

from musicxml_engine import MusicXMLEngine

mxml = MusicXMLEngine()


def seed():
    for s in music21.corpus.chorales.Iterator():
        raw = open(s.write(), "rb").read()
        meta = mxml.meta(raw)
        thumbnail = mxml.thumbnail(raw)
        response = requests.post('https://pb.vimu.app/api/collections/score_meta/records',
                                 json=meta)
        if response.ok:
            score_meta = json.loads(response.text)

            files = {
                'data': raw,
                'thumbnail': thumbnail
            }
            data = {
                'name': s.metadata.bestTitle,
                'meta': score_meta['id'],
                'public': True
            }
            response = requests.post('https://pb.vimu.app/api/collections/scores/records',
                                     files=files, data=data)

            print(s.metadata.bestTitle)


if __name__ == '__main__':
    seed()