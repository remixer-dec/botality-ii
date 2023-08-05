from utils import cprint
try:
  import torch
  from audiocraft.models import MusicGen, AudioGen
  from audiocraft.data.audio import audio_write
  tta_available = True
except ImportError:
  AudioGen = None
  MusicGen = None
  tta_available = False
  cprint("TTA (AudioCraft) module not available, please reinstall it", color="red")

from concurrent.futures import ThreadPoolExecutor
import asyncio
import tempfile
from config_reader import config

models = {}

def get_model(path, loader):
  if path in models:
    model = models[path]
  else:
    model = loader.get_pretrained(path, config.tta_device)
    models[path] = model
  return model


def generate_audio(text, audio_type="music", duration=5, raw_data=False):
  try:
    if audio_type == "music":
      model = get_model(config.tta_music_model, MusicGen)
    else:
      model = get_model(config.tta_sfx_model, AudioGen)
    model.set_generation_params(duration=duration)
    wav = model.generate([text])
  except Exception as e:
    return (str(e), None)
  if not raw_data:
    wav = save_audio(wav[0], model)
  return False, wav

async def generate_audio_async(text, audio_type="music", duration=5, raw_data=False):
  with ThreadPoolExecutor():
    error, output = await asyncio.to_thread(generate_audio, 
      text, audio_type, duration, raw_data
    )
  return error, output

  
def save_audio(wav_file, model):
  tmp_path = tempfile.TemporaryDirectory().name + 'record'
  audio_write(tmp_path, wav_file.cpu(), model.sample_rate, strategy="loudness", loudness_compressor=True)
  return tmp_path + '.wav'