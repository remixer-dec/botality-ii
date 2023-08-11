from whispercpp import Whisper
from providers.stt.abstract_stt import AbstractSTT
from config_reader import config
from concurrent.futures import ThreadPoolExecutor
from misc.memory_manager import mload
from functools import partial
import asyncio

class WhisperCPP(AbstractSTT):
  def __init__(self):
    if config.mm_preload_models_on_start:
      m = self.model

  @property
  def model(self):
    loader = partial(Whisper, config.stt_model_path_or_name)
    return mload('stt-whisper', loader, None)
  
  async def recognize(self, audio_path):
    try:
      with ThreadPoolExecutor():
        output = await asyncio.to_thread(self.model.transcribe, audio_path)
      text = ''.join(self.model.extract_text(output))
      return False, text
    except Exception as e:
      return str(e), None 

init = WhisperCPP