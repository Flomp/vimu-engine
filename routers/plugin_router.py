import random
import traceback

from fastapi import APIRouter

from models.api import APIResponse
from models.plugin import Plugin, SocketType

router = APIRouter()


@router.post('/plugin/test')
def test_plugin(plugin: Plugin):
    loc = {}
    input_data = {}
    output_data = {}
    logs = "Generating input data...\n"
    for i in plugin.config.inputs:
        if i.type == SocketType.number:
            input_data[i.key] = random.randint(1, 100)
    logs += "====== Success ✓ ======\n"
    try:
        logs += "Executing code...\n"
        exec(plugin.code, {'input_data': input_data, 'output_data': output_data}, loc)
        logs += "====== Success ✓ ======\n"
        logs += "Validating outputs...\n"
        for o in plugin.config.outputs:
            if o.type == SocketType.number:
                assert isinstance(output_data[o.key], int), f"{o.key} must be of type int"
        logs += "====== Success ✓ ======\n"
    except Exception as e:
        logs += "====== Failure X ======\n"
        logs += f"______ {type(e).__name__} ______\n"
        logs += traceback.format_exc()

        return APIResponse(status="error", data={"input": input_data, "output": output_data, "logs": logs},
                           error=str(e))
    logs += "====== All tests passed ======"
    return APIResponse(status="success", data={"input": input_data, "output": output_data, "logs": logs}, error=None)
