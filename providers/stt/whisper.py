from whispercpp import Whisper
from providers.stt.abstract_stt import AbstractSTT
from config_reader import config
from concurrent.futures import ThreadPoolExecutor
import asyncio

class WhisperCPP(AbstractSTT):
  def __init__(self):
    self.model = Whisper(config.stt_model_path_or_name)
  
  async def recognize(self, audio_path):
    try:
      with ThreadPoolExecutor():
        output = await asyncio.to_thread(self.model.transcribe, audio_path)
      text = ''.join(self.model.extract_text(output))
      return False, text
    except Exception as e:
      return str(e), None 

init = WhisperCPP