from providers.tts import tts_backends
from config_reader import config
from providers.tts.abstract_tts import AbstractSTS
import os
import subprocess

tts_backends_active = []
tts_voicemap = {}
sts_voicemap = {}

async def tts(voice, text):
  if voice in tts_voicemap:
    return await tts_voicemap[voice].speak(voice, text)
  return ('Voice not found', None)

async def sts(voice, original_audio=False):
  if voice in sts_voicemap:
    return await tts_voicemap[voice].mimic(voice, original_audio)
  return ('Voice not found', None)

def init():
  if 'tts' in config.active_modules:
    for backend in tts_backends:
      is_sts = issubclass(tts_backends[backend], AbstractSTS)
      args = [tts] if is_sts else []
      b = tts_backends[backend](*args)
      if b.is_available:
        tts_backends_active.append(b)
        for voice in b.voices:
          tts_voicemap[voice] = b
          if is_sts:
            sts_voicemap[voice] = b

def remote_tts(*args, **kwargs):
  pass

def convert_to_ogg(wav_path):
  ogg_path = wav_path + '.ogg'
  subprocess.run([
    config.tts_ffmpeg_path, '-i', wav_path, 
    '-acodec', 'libopus', '-b:a', '128k', '-vbr', 'off', ogg_path, '-y'],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.STDOUT
  )
  with open(ogg_path, 'rb') as f:
    data = f.read()  
  os.remove(wav_path)
  os.remove(ogg_path)
  return data