import asyncio
import random
import traceback
from datetime import datetime

import music21.stream.base
from fastapi import APIRouter
from music21 import corpus
from starlette.concurrency import run_in_threadpool

from models.api import APIResponse
from models.plugin import SocketType, TestPluginRequest, PluginSocket

router = APIRouter()
from io import StringIO
from contextlib import redirect_stdout

@router.post('/plugin/test')
async def test_plugin(plugin_request: TestPluginRequest):
    logs = []
    try:
        return await asyncio.wait_for(run_in_threadpool(run_plugin_test, plugin_request, logs), timeout=10.0)
    except asyncio.TimeoutError as e:
        append_log(logs, "====== Failure X ======", "error")
        append_log(logs, f"______ {type(e).__name__} ______", "error")
        append_log(logs, traceback.format_exc(), "error")

        return APIResponse(status="error", data={"logs": logs},
                           error=str(e))


def run_plugin_test(plugin_request: TestPluginRequest, logs: list):
    loc = {}
    input_data = {}
    output_data = {}
    append_log(logs, "Generating input data...")
    for i in plugin_request.plugin.config.inputs:
        generate_input(i, input_data)
    append_log(logs, "====== Success ✓ ======")

    try:
        append_log(logs, "Executing code...")
        f = StringIO()
        with redirect_stdout(f):
            exec(plugin_request.plugin.code,
                 {'input_data': input_data, 'node': plugin_request.node, 'output_data': output_data}, loc)

        code_logs = f.getvalue().split('\n')[:-1]
        for log in code_logs:
            append_log(logs, log)

        append_log(logs, "====== Success ✓ ======")
        append_log(logs, "Validating outputs...")
        for o in plugin_request.plugin.config.outputs:
            validate_output(o, output_data)
        append_log(logs, "====== Success ✓ ======")
    except Exception as e:
        append_log(logs, "====== Failure X ======", "error")
        append_log(logs, f"______ {type(e).__name__} ______", "error")
        append_log(logs, traceback.format_exc(), "error")

        return APIResponse(status="error", data={"logs": logs},
                           error=str(e))
    append_log(logs, "====== All tests passed ======", "success")
    return APIResponse(status="success", data={"logs": logs}, error=None)


def generate_input(i: PluginSocket, input_data: dict):
    if i.type == SocketType.int:
        input_data[i.key] = random.randint(1, 100)
    elif i.type == SocketType.float:
        input_data[i.key] = random.uniform(0, 10)
    elif i.type == SocketType.string:
        input_data[i.key] = ("In the beginning the Universe was created. This had made many people very angry and has "
                             "been widely regarded as a bad move.")
    elif i.type == SocketType.list:
        input_data[i.key] = []
    elif i.type == SocketType.set:
        input_data[i.key] = set()
    elif i.type == SocketType.dict:
        input_data[i.key] = dict()
    elif i.type == SocketType.stream:
        input_data[i.key] = corpus.parse('bwv66.6')
    elif i.type == SocketType.score:
        input_data[i.key] = corpus.parse('bwv66.6')
    elif i.type == SocketType.part:
        input_data[i.key] = corpus.parse('bwv66.6').parts[0]
    elif i.type == SocketType.object:
        input_data[i.key] = corpus.parse('bwv66.6')


def validate_output(o: PluginSocket, output_data: dict):
    assert o.key in output_data, f"{o.key} not found in output_data"
    if o.type == SocketType.int:
        assert type(output_data[o.key]) is int, f"{o.key} must be of type int, is type {type(output_data[o.key])}"
    elif o.type == SocketType.float:
        assert type(output_data[o.key]) is float, f"{o.key} must be of type float, is type {type(output_data[o.key])}"
    elif o.type == SocketType.string:
        assert type(output_data[o.key]) is str, f"{o.key} must be of type str, is type {type(output_data[o.key])}"
    elif o.type == SocketType.bool:
        assert type(output_data[o.key]) is bool, f"{o.key} must be of type bool, is type {type(output_data[o.key])}"
    elif o.type == SocketType.list:
        assert type(output_data[o.key]) is list, f"{o.key} must be of type list, is type {type(output_data[o.key])}"
    elif o.type == SocketType.set:
        assert type(output_data[o.key]) is set, f"{o.key} must be of type set, is type {type(output_data[o.key])}"
    elif o.type == SocketType.dict:
        assert type(output_data[o.key]) is dict, f"{o.key} must be of type dict, is type {type(output_data[o.key])}"
    elif o.type == SocketType.stream:
        assert isinstance(output_data[o.key],
                          music21.stream.base.Stream), f"{o.key} must be of type music21.stream.base.Stream, is type {type(output_data[o.key])}"
    elif o.type == SocketType.score:
        assert isinstance(output_data[o.key],
                          music21.stream.Score), f"{o.key} must be of type music21.stream.Score, is type {type(output_data[o.key])}"
    elif o.type == SocketType.part:
        assert isinstance(output_data[o.key],
                          music21.stream.Part), f"{o.key} must be of type music21.stream.Part, is type {type(output_data[o.key])}"
    elif o.type == SocketType.object:
        assert isinstance(output_data[o.key],
                          music21.base.Music21Object), f"{o.key} must be of type music21.base.Music21Object, is type {type(output_data[o.key])}"


def append_log(logs, text, level="info"):
    logs.append({
        "date": datetime.now(),
        "level": level,
        "text": text
    })
