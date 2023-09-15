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

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu') # do not use MPS, currently it is bugged

class CoquiTTS(AbstractTTS):
  def __init__(self):
    self.name = 'coqui_tts'
    self.voices = config.tts_voices
    try:
      from TTS.api import TTS
      self.TTS = TTS
      self.is_available = True
    except Exception:
      self.is_available = False
      if 'tts' in config.active_modules and config.tts_mode == 'local':
        cprint("CoquiTTS provider not available", color="red")
  
  def _speak(self, voice, text):
    voic_model_loader = partial(
      self.TTS,
      model_path =  Path(config.tts_path) / (voice + ".pth"), 
      config_path = Path(config.tts_path) / "config.json"
    )
    loaded_model = mload('CoquiTTS-' + voice, voic_model_loader, None, gpu=torch.cuda.is_available())
    if (loaded_model.synthesizer.tts_model.device.type != device.type):
      loaded_model.synthesizer.tts_model = loaded_model.synthesizer.tts_model.to(device)
    tmp_path = tempfile.TemporaryDirectory().name + 'record.wav'
    if loaded_model.model_name is None:
      loaded_model.model_name = voice
    loaded_model.tts_to_file(text, file_path=tmp_path)
    return tmp_path

  async def speak(self, voice, text):
    try:
      with ThreadPoolExecutor():
        wav_file_path = await asyncio.to_thread(self._speak, voice, text + '.')
      return False, wav_file_path
    except RuntimeWarning as e:
      return str(e), None 
