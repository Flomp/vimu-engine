import os

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from routers import musicxml_router, engine_router, plugin_router

app = FastAPI()

origins = [settings.app_url]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(engine_router.router)
app.include_router(musicxml_router.router)
if settings.allow_plugins:
    app.include_router(plugin_router.router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=os.getenv("PORT", default=5000), log_level="info")
