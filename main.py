import io
import json
import os

import music21.converter
import uvicorn

from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import StreamingResponse

from engine import Engine, EngineException
from models.api import APIResponse
from models.engine import Data
from musicxml import MusicXML

app = FastAPI()
engine = Engine()
musicxml = MusicXML()

origins = [os.getenv("APP_URL", "https://vimu.app")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/engine", response_model=APIResponse)
async def root(data: Data):
    try:
        data = engine.process(data)
        return APIResponse("success", data, None)
    except EngineException as e:

        return APIResponse("error", None, {"message": str(e), "node": e.node})


@app.post("/musicxml/meta")
async def musicxml_meta(file: UploadFile):
    try:
        meta = musicxml.meta(file.file.read())
    except music21.converter.ConverterException:
        raise HTTPException(status_code=400, detail="Bad request")
    return APIResponse("success", meta, None)


@app.post("/musicxml/thumbnail")
async def musicxml_thumbnail(file: UploadFile):
    thumbnail = musicxml.thumbnail(file.file.read())
    return StreamingResponse(io.BytesIO(thumbnail), media_type="image/svg+xml")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=os.getenv("PORT", default=5000), log_level="info")
