from providers.tts.abstract_tts import AbstractTTS
from config_reader import config
from concurrent.futures import ThreadPoolExecutor
import asyncio
import subprocess
import tempfile
import sys 
import os

class Say(AbstractTTS):
  def __init__(self, is_remote):
    self.is_available = sys.platform == "darwin"
    self.system = True
    self.name = 'say_macos'
    self.authors = ['Apple']
    self.voices = [
      'Alex', 'Alice', 'Alva', 'Amelie', 'Anna', 'Carmit', 'Damayanti', 'Daniel', 'Diego',
      'Ellen', 'Fiona', 'Fred', 'Ioana', 'Joana', 'Jorge', 'Juan', 'Kanya', 'Karen',
      'Kyoko', 'Laura', 'Lekha', 'Luca', 'Luciana', 'Maged', 'Mariska', 'Mei-Jia',
      'Melina', 'Milena', 'Moira', 'Monica', 'Nora', 'Paulina', 'Rishi', 'Samantha',
      'Sara', 'Satu', 'Sin-ji', 'Tessa', 'Thomas', 'Ting-Ting', 'Veena', 'Victoria',
      'Xander', 'Yelda', 'Yuna', 'Yuri', 'Zosia', 'Zuzana'
    ]
    self.voice_metamap = dict(zip(
      self.voices,
      [{"lang": lang, "tone": tone} for lang, tone in [
        ('en','m'), ('it','f'), ('sv','f'), ('fr','f'), ('de','f'), ('he','f'), ('id','f'), ('en','m'), ('es','m'),
        ('nl','f'), ('en','f'), ('en','m'), ('ro','f'), ('pt','f'), ('es','m'), ('es','m'), ('th','f'), ('en','f'),
        ('ja','f'), ('sk','f'), ('hi','f'), ('it','m'), ('pt','f'), ('ar','m'), ('hu','f'), ('zh','f'),
        ('el','f'), ('ru','f'), ('en','f'), ('es','f'), ('nb','f'), ('es','f'), ('en','m'), ('en','f'),
        ('da','f'), ('fi','f'), ('zh','f'), ('en','m'), ('fr','m'), ('zh','f'), ('en','f'), ('en','f'), 
        ('nl','m'), ('tr','f'), ('ko','f'), ('ru','m'), ('pl','f'), ('cs','f')
      ]]
    ))

  def _speak(self, voice, text):
    tmp_path_aiff = tempfile.TemporaryDirectory().name + 'record.aif'
    tmp_path_wav = tmp_path_aiff.replace('.aif', '.wav')
    subprocess.run(
      ['say','-v', voice,  '-o', tmp_path_aiff, text],
    )
    subprocess.run([
      config.tts_ffmpeg_path, '-y', '-i', tmp_path_aiff, tmp_path_wav],
      stdout=subprocess.DEVNULL,
      stderr=subprocess.STDOUT
    )
    os.unlink(tmp_path_aiff)
    return tmp_path_wav

  async def speak(self, voice, text):
    try:
      with ThreadPoolExecutor():
        wav_file_path = await asyncio.to_thread(self._speak, voice, text)
      return False, wav_file_path
    except Exception as e:
      return str(e), None 
