from providers.tts import tts_backends, RemoteTTS
from config_reader import config
from providers.tts.abstract_tts import AbstractSTS
import threading
import os
import subprocess
import logging
logger = logging.getLogger(__name__)

tts_voicemap = {}
system_voicemap = {}
sts_voicemap = {}
tts_backends_loaded = {}
tts_authors = set()

remote_tts = None

async def tts(voice, text):
  if remote_tts and remote_tts.is_available:
    backend = remote_tts
  elif voice in tts_voicemap:
    backend = tts_voicemap[voice]
  else:
    return ('Voice not found', None)
  return await backend.speak(voice, text)

async def sts(voice, original_audio=False):
  if voice in sts_voicemap:
    return await sts_voicemap[voice].mimic(voice, original_audio)
  return ('Voice not found', None)

def init(allowRemote=True, threaded=True):
  global remote_tts
  threads = []
  if 'tts' in config.active_modules:
    for backend in tts_backends:
      if backend not in config.tts_enable_backends:
        continue
      if not threaded:
        init_backend(backend, allowRemote)
        continue
      thread = threading.Thread(target=init_backend, args=(backend, allowRemote))
      thread.start()
      threads.append(thread)
    for thread in threads:
      thread.join()
    if allowRemote:
      remote_tts = RemoteTTS()
  return 

def init_backend(backend, remote):
  is_sts = issubclass(tts_backends[backend], AbstractSTS)
  args = [tts, remote] if is_sts else [remote]
  b = tts_backends[backend](*args)
  if b.is_available:
    logger.debug('tts backend initialized: ' + backend)
  if b.is_available or config.tts_mode != 'local':
    tts_backends_loaded[backend] = b
    for voice in b.voices:
      tts_voicemap[voice] = b
      if is_sts:
        sts_voicemap[voice] = b
      if b.system:
        system_voicemap[voice] = b
    for author in b.authors:
      if author is not None:
        tts_authors.add(author)
  return b

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