import hashlib
import json

import aioredis
from fastapi import APIRouter, Request

from config import settings
from engine import Engine, EngineException
from models.api import APIResponse
from models.engine import Data

router = APIRouter()
engine = Engine()
redis = aioredis.from_url(settings.redis_url,
                          encoding="utf8", decode_responses=True) if settings.redis_url is not None else None


@router.post("/engine", response_model=APIResponse)
async def root(data: Data, request: Request) -> APIResponse:
    try:
        body = await request.body()
        request_hash = hashlib.sha256(body).hexdigest()
        cached_data = await redis.get(request_hash) if redis is not None else None
        if cached_data is not None:
            processed_data = {
                'output': json.loads(cached_data),
                'plots': []
            }
        else:
            processed_data = engine.process(data)
            # we cannot cache figured_bass_realize because its outcome is non-deterministic
            if redis is not None and processed_data['output'] is not None and len(
                    processed_data['plots']) == 0 and not _contains_figured_bass_node(data):
                await redis.set(request_hash, json.dumps(processed_data['output']))
        return APIResponse(status="success", data=processed_data, error=None)
    except EngineException as e:

        return APIResponse(status="error", data=None, error={"message": str(e), "node": e.node})


def _contains_figured_bass_node(data: Data):
    return any(map(lambda n: n.name == 'figured_bass_realize', data.nodes.values()))
