import sys 
sys.path.append('.')
sys.path.append('..')
from fastapi import FastAPI
from providers.tts_provider import tts, save_audio
import base64
from pydantic import BaseModel
import numpy as np

app = FastAPI()

class Data(BaseModel):
  voice: str
  text: str



@app.post("/")
async def read_root(rqdata: Data):
  status, data = await tts(rqdata.voice, rqdata.text)
  if status:
    return {"data": data}
  else:
    return {"error": data}

if __name__ == "__main__":
  import uvicorn
  uvicorn.run(app, host="0.0.0.0", port=7077)
  