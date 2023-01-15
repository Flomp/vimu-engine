import os

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from engine import Engine, EngineException
from models.api import APIResponse
from models.engine import Data
from routers import stripe_router, musicxml_router

app = FastAPI()
engine = Engine()

origins = [settings.app_url]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(stripe_router.router)
app.include_router(musicxml_router.router)


@app.post("/engine", response_model=APIResponse)
async def root(data: Data):
    try:
        data = engine.process(data)
        return APIResponse("success", data, None)
    except EngineException as e:

        return APIResponse("error", None, {"message": str(e), "node": e.node})


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=os.getenv("PORT", default=5000), log_level="info")
