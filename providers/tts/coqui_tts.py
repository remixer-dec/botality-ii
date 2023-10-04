from providers.tts.abstract_tts import AbstractTTS
from config_reader import config
from concurrent.futures import ThreadPoolExecutor
from misc.memory_manager import mload
from functools import partial
from utils import cprint
from pathlib import Path
import asyncio
import torch
import tempfile
import logging
import os
logger = logging.Logger(__name__)

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu') # do not use MPS, currently it is bugged

class CoquiTTS(AbstractTTS):
  def __init__(self, is_remote):
    self.name = 'coqui_tts'
    self.voices = list(map(lambda item: item if isinstance(item, str) else item.get('voice'), config.tts_voices))
    self.system = False
    self.is_available = False
    if is_remote:
      return
    try:
      from TTS.api import TTS
      self.TTS = TTS
      self.is_available = True
    except Exception as e:
      logger.error(e)
      if 'tts' in config.active_modules and config.tts_mode == 'local':
        cprint("CoquiTTS provider not available", color="red")
  
  def _speak(self, voice, text):
    config_path = Path(config.tts_path) / (voice + ".json")
    config_path = Path(config.tts_path) / "config.json" if not os.path.exists(config_path) else config_path
    voic_model_loader = partial(
      self.TTS,
      model_path  = Path(config.tts_path) / (voice + ".pth"),       
      config_path = config_path
    )
    loaded_model = mload('CoquiTTS-' + voice, voic_model_loader, None, gpu=torch.cuda.is_available())
    if (loaded_model.synthesizer.tts_model.device.type != device.type):
      loaded_model.synthesizer.tts_model = loaded_model.synthesizer.tts_model.to(device)
    tmp_path = tempfile.TemporaryDirectory().name + 'record.wav'
    if hasattr(loaded_model, 'model_name') and loaded_model.model_name is None:
      loaded_model.model_name = voice
    loaded_model.tts_to_file(text, file_path=tmp_path)
    return tmp_path

  async def speak(self, voice, text):
    try:
      with ThreadPoolExecutor():
        wav_file_path = await asyncio.to_thread(self._speak, voice, text + '.')
      return False, wav_file_path
    except Exception as e:
      return str(e), None 
