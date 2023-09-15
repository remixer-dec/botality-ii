from providers.tts.abstract_tts import AbstractSTS
from config_reader import config
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import asyncio
import subprocess
import tempfile
import sys 
import os
import time

class SoVitsSVC(AbstractSTS):
  def __init__(self, tts_instance):
    self.tts = tts_instance
    self.voices = dict({m['voice'].lower().replace('-',''): m for m in config.tts_so_vits_svc_voices})
    self.v4_0_code_path = config.tts_so_vits_svc_4_0_code_path
    self.v4_1_code_path = config.tts_so_vits_svc_4_1_code_path
    self.v4_0_available = os.path.exists(self.v4_0_code_path)
    self.v4_1_available = os.path.exists(self.v4_1_code_path)
    self.is_available = self.v4_0_available or self.v4_1_available

  def _mimic(self, voice, original_audio_path):
    version = self.voices[voice].get('v', 4.0)
    so_vits_svc_code = self.v4_0_code_path if version == 4.0 else self.v4_1_code_path
    name = 'temp_tts' + str(time.time_ns())
    temp_file = f'{so_vits_svc_code}/raw/{name}.wav'
    os.rename(original_audio_path, temp_file)
    v = self.voices[voice]
    so_vits_model = Path(v['path']) / v['weights']
    so_vits_config = Path(v['path']) / 'config.json'
    so_vits_voice = v['voice']
    subprocess.run([
      config.python_command, 
      f"inference_main.py", 
      "-m", str(so_vits_model), 
      "-c", str(so_vits_config), 
      "-n", f'{name}.wav', 
      "-t", "0", 
      "-s", so_vits_voice
      ],
    cwd=so_vits_svc_code
    )
    os.remove(temp_file)
    filename = f'{so_vits_svc_code}/results/{name}.wav_0key_{so_vits_voice}.flac'
    if not os.path.isfile(filename):
      filename = filename.replace('.flac', '_sovits_pm.flac')
      if not os.path.isfile(filename):
        raise Exception('File not found')
    return filename

  async def speak(self, voice, text):
    error, original_audio = await self.tts(self.voices[voice].get('base_voice'), text)
    if not error:
      return await self.mimic(voice, original_audio)
    return error, None

  async def mimic(self, voice, original_audio_path):
    try:
      with ThreadPoolExecutor():
        wav_file_path = await asyncio.to_thread(self._mimic, voice, original_audio_path)
      return False, wav_file_path
    except Exception as e:
      return str(e), None 
