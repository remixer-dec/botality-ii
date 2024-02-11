from providers.stt.abstract_stt import AbstractSTT
from config_reader import config
from concurrent.futures import ThreadPoolExecutor
from misc.memory_manager import mload
from functools import partial
from utils import cprint
import torch
import asyncio
try:
  import whisper_s2t
except ImportError:
  whisper_s2t = False

class WhisperS2T(AbstractSTT):
  def __init__(self):
    if not whisper_s2t:
      cprint("WhisperS2T (STT) module not available, please reinstall it", color="red")
    if config.mm_preload_models_on_start:
      m = self.model

  @property
  def model(self):
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(device)
    ct = 'int8' if device != 'cuda' else 'float16'
    backend = config.stt_backend.split('_')[1]
    loader = partial(whisper_s2t.load_model, config.stt_model_path_or_name, backend=backend, device=device, compute_type=ct)
    return mload('stt-whisper_s2t', loader, None)
  
  async def recognize(self, audio_path):
    try:
      with ThreadPoolExecutor():
        output = await asyncio.to_thread(self.model.transcribe_with_vad, [audio_path], lang_codes=[config.lang], tasks=['transcribe'], initial_prompts=[None], batch_size=1)
      text = output[0][0]['text']
      return False, text
    except Exception as e:
      return str(e), None 
init = WhisperS2T