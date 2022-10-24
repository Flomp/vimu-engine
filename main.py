from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from engine.engine import Engine
from models.api import APIResponse
from models.engine import Data

app = FastAPI()
engine = Engine()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/", response_model=APIResponse)
async def root(data: Data):
    data = engine.process(data)

    return APIResponse("success", data, None)
