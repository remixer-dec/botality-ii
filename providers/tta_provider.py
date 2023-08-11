from utils import cprint
from config_reader import config
from concurrent.futures import ThreadPoolExecutor
from misc.memory_manager import mload
from functools import partial
import asyncio
import tempfile

AudioGen = None
MusicGen = None

def tta_init():
  global MusicGen, AudioGen, audio_write
  try:
    from audiocraft.models import MusicGen, AudioGen
    from audiocraft.data.audio import audio_write
    return True
  except ImportError:
    cprint("TTA (AudioCraft) module not available, please reinstall it", color="red")
    return False

def get_model(path, loader, name):
  loader = partial(loader.get_pretrained, path, config.tta_device)
  model = mload('tta-' + name, loader, None)
  return model


def generate_audio(text, audio_type="music", duration=5, raw_data=False):
  try:
    if audio_type == "music":
      model = get_model(config.tta_music_model, MusicGen, 'MusicGen')
    else:
      model = get_model(config.tta_sfx_model, AudioGen, 'AudioGen')
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