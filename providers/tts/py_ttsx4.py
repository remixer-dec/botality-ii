from providers.tts.abstract_tts import AbstractTTS
from config_reader import config
from concurrent.futures import ThreadPoolExecutor
import asyncio
import tempfile
import sys 
import logging
logger = logging.Logger(__name__)

class TTSx4(AbstractTTS):
  def __init__(self, is_remote):
    self.system = True
    self.voices = []
    self.authors = []
    self.is_available = False
    self.name = 'ttsx4'
    if is_remote:
      return
    try:
      import pyttsx4
      self.engine = pyttsx4.init()
      self.prefix = 'com.apple.speech.synthesis.voice.' if sys.platform == "darwin" else ''
      self.voices = [v.name for v in self.engine.getProperty('voices')]
      self.is_available = True
      self.voice_metamap = {
        v.name: 
        {
          "lang": v.languages[0][:2], 
          "tone": 'f' if v.gender == 'VoiceGenderFemale' else 'm' if v.gender == 'VoiceGenderMale' else '*'
        }
        for v in self.engine.getProperty('voices')
      }
    except Exception as e:
      logger.error(e)

  def _speak(self, voice, text):
    tmp_path = tempfile.TemporaryDirectory().name + 'record.wav'
    self.engine.setProperty('voice', self.prefix + voice)
    self.engine.save_to_file(text, tmp_path)
    self.engine.runAndWait()
    return tmp_path

  async def speak(self, voice, text):
    try:
      with ThreadPoolExecutor():
        wav_file_path = await asyncio.to_thread(self._speak, voice, text)
      return False, wav_file_path
    except Exception as e:
      return str(e), None 
