import sys 
import os
import asyncio
from fastapi import FastAPI
from pydantic import BaseModel, Field
from fastapi.responses import StreamingResponse
from io import BytesIO
from typing_extensions import Literal
sys.path.append('.')
sys.path.append('..')
from providers.tts_provider import init, tts


# polyfill for python3.8
if not hasattr(asyncio, 'to_thread'):
  import functools
  import contextvars
  async def to_thread(func, /, *args, **kwargs):
    loop = asyncio.get_running_loop()
    ctx = contextvars.copy_context()
    func_call = functools.partial(ctx.run, func, *args, **kwargs)
    return await loop.run_in_executor(None, func_call)
  asyncio.to_thread = to_thread

app = FastAPI()

class Data(BaseModel):
  voice: str = Field(None, description='String with speaker model name')
  text: str = Field(None, description='String with text that you want to hear')
  response: Literal['file', 'path'] = Field(None, description='String with value "file" or "path", changes the output format to either the path to the recorded audio or the file itself.')


@app.post("/")
async def read_root(rqdata: Data):
  error, data = await tts(rqdata.voice, rqdata.text)
  if not error:
    if rqdata.response == 'file':
      bytes = BytesIO(open(data, mode='rb').read())
      os.remove(data)
      response = StreamingResponse(bytes, media_type='audio/wav')
      response.headers["Content-Disposition"] = f"inline; filename=record.wav"
      return response
    return {"data": data}
  else:
    return {"error": error}

if __name__ == "__main__":
  import uvicorn
  init(allowRemote=False)
  uvicorn.run(app, host="0.0.0.0", port=7077)
  