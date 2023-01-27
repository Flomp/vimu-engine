import io

import music21.converter
from fastapi import UploadFile, HTTPException, APIRouter
from starlette.responses import StreamingResponse, Response

from models.api import APIResponse
from musicxml_engine import MusicXMLEngine

router = APIRouter()
musicxml_engine = MusicXMLEngine()


@router.post("/musicxml/convert")
async def musicxml_convert(file: UploadFile):
    musicxml_file = musicxml_engine.convert(file.file.read())
    return Response(musicxml_file, media_type="application/xml")


@router.post("/musicxml/meta")
async def musicxml_meta(file: UploadFile):
    try:
        meta = musicxml_engine.meta(file.file.read())
    except music21.converter.ConverterException as e:
        raise HTTPException(status_code=400, detail="Bad request")
    return APIResponse("success", meta, None)


@router.post("/musicxml/thumbnail")
async def musicxml_thumbnail(file: UploadFile):
    thumbnail = musicxml_engine.thumbnail(file.file.read())
    return Response(thumbnail, media_type="image/svg+xml")
