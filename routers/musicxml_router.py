import io

import music21.converter
from fastapi import UploadFile, HTTPException, APIRouter
from starlette.responses import StreamingResponse

from models.api import APIResponse
from musicxml_engine import MusicXMLEngine

router = APIRouter()
musicxml_engine = MusicXMLEngine()


@router.post("/musicxml/meta")
async def musicxml_meta(file: UploadFile):
    try:
        meta = musicxml_engine.meta(file.file.read())
    except music21.converter.ConverterException:
        raise HTTPException(status_code=400, detail="Bad request")
    return APIResponse("success", meta, None)


@router.post("/musicxml/thumbnail")
async def musicxml_thumbnail(file: UploadFile):
    thumbnail = musicxml_engine.thumbnail(file.file.read())
    return StreamingResponse(io.BytesIO(thumbnail), media_type="image/svg+xml")