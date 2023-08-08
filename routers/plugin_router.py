import random
import traceback
from datetime import datetime

import music21.stream.base
from fastapi import APIRouter
from music21 import corpus

from models.api import APIResponse
from models.plugin import SocketType, TestPluginRequest

router = APIRouter()


@router.post('/plugin/test')
def test_plugin(plugin_request: TestPluginRequest):
    loc = {}
    input_data = {}
    output_data = {}
    logs = []
    append_log(logs, "Generating input data...")
    for i in plugin_request.plugin.config.inputs:
        if i.type == SocketType.number:
            input_data[i.key] = random.randint(1, 100)
        elif i.type == SocketType.stream:
            input_data[i.key] = corpus.parse('bwv66.6')
    append_log(logs, "====== Success ✓ ======")

    try:
        append_log(logs, "Executing code...")
        exec(plugin_request.plugin.code,
             {'input_data': input_data, 'node': plugin_request.node, 'output_data': output_data}, loc)
        append_log(logs, "====== Success ✓ ======")
        append_log(logs, "Validating outputs...")
        for o in plugin_request.plugin.config.outputs:
            if o.type == SocketType.number:
                assert type(output_data[o.key]) is int, f"{o.key} must be of type int"
            elif o.type == SocketType.stream:
                assert isinstance(output_data[o.key],
                                  music21.stream.base.Stream), f"{o.key} must be of type music21.stream.base.Stream"
        append_log(logs, "====== Success ✓ ======")
    except Exception as e:
        append_log(logs, "====== Failure X ======", "error")
        append_log(logs, f"______ {type(e).__name__} ______", "error")
        append_log(logs, traceback.format_exc(), "error")

        return APIResponse(status="error", data={"logs": logs},
                           error=str(e))
    append_log(logs, "====== All tests passed ======", "success")
    return APIResponse(status="success", data={"logs": logs}, error=None)


def append_log(logs, text, level="info"):
    logs.append({
        "date": datetime.now(),
        "level": level,
        "text": text
    })
