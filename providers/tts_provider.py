from utils import cprint
from config_reader import config
try:
  import torch
  from TTS.utils.synthesizer import Synthesizer
except ImportError:
  Synthesizer = None
  if 'tts' in config.active_modules and config.tts_mode == 'local':
    cprint("TTS module not available, please reinstall it", color="red")
from pathlib import Path
import httpx
import json
import tempfile
import subprocess
import os
import time
from config_reader import config
from misc.memory_manager import mload
from functools import partial

synthesizers = {}
so_vits_svc_voices = dict({m['voice'].lower().replace('-',''): m for m in config.tts_so_vits_svc_voices})

async def so_vits_svc(voice, text, original_audio=False):
  version = so_vits_svc_voices[voice].get('v', 4.0)
  v4_0_code_path = config.tts_so_vits_svc_4_0_code_path
  v4_1_code_path = config.tts_so_vits_svc_4_1_code_path
  so_vits_svc_code = v4_0_code_path if version == 4.0 else v4_1_code_path
  name = 'temp_tts' + str(time.time_ns())
  temp_file = f'{so_vits_svc_code}/raw/{name}.aif'
  temp_file_wav = temp_file.replace('.aif', '.wav')
  v = so_vits_svc_voices[voice]
  so_vits_model = Path(v['path']) / v['weights']
  so_vits_config = Path(v['path']) / 'config.json'
  so_vits_voice = v['voice']
  base_voice = v['base_voice']
  if not original_audio:
    # generate any text-to-speech output
    base_tts_provider = v.get('provider', config.tts_so_vits_svc_base_tts_provider)
    if base_tts_provider == 'say_macos':
      subprocess.run(
        ['say','-v', base_voice,  '-o', temp_file, text],
      )
    elif base_tts_provider == 'built_in':
      error, temp_file = await tts(base_voice, text)
  else:
    temp_file = original_audio

  subprocess.run([
    config.tts_ffmpeg_path, '-y', '-i', temp_file, temp_file_wav],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.STDOUT
  )
  subprocess.run(
    [config.python_command, f"inference_main.py", "-m", str(so_vits_model), "-c", str(so_vits_config), 
    "-n", f'{name}.wav', "-t", "0", "-s", so_vits_voice]
    ,
    cwd=so_vits_svc_code
  )
  os.remove(temp_file)
  os.remove(temp_file_wav)
  filename = f'{so_vits_svc_code}/results/{name}.wav_0key_{so_vits_voice}.flac'
  if not os.path.isfile(filename):
    filename = filename.replace('.flac', '_sovits_pm.flac')
    if not os.path.isfile(filename):
      return ('File not found', None)
  return (False, filename)

async def tts(voice, text):
  try:
    assert os.path.exists(config.tts_ffmpeg_path)
    for r in config.tts_replacements:
      text = text.replace(r, config.tts_replacements[r])
    if voice in so_vits_svc_voices:
      return await so_vits_svc(voice, text)
    loader = partial(
      Synthesizer,
      tts_config_path=Path(config.tts_path) / "config.json",
      tts_checkpoint=Path(config.tts_path) / (voice + ".pth"),
      use_cuda=torch.cuda.is_available(),
    )
    synth = mload('tts-' + voice, loader, None, gpu=torch.cuda.is_available())
    data = synth.tts(text[:4096] + '.')
    return (False, save_audio(synth, data))
  except Exception as e:
    return (str(e), None)

async def remote_tts(voice, text):
  async with httpx.AsyncClient() as client:
    try:
      tts_payload = {"voice": voice, "text": text, "response": 'file' if config.tts_mode == 'remote' else 'path'}
      response = await client.post(url=config.tts_host, json=tts_payload, timeout=None)
      if response.status_code == 200:
        if config.tts_mode == 'remote':
          path = tempfile.TemporaryDirectory().name + str(hash(text)) + '.wav'
          with open(path, 'wb') as f:
            f.write(response.content)
          return (False, path)
        else:
          response_data = response.json()
        error = response_data.get('error')
        if error:
          return (error, None)
        wpath = response_data.get("data")
        return (False, wpath)
      else:
        return ('Server error', None)
    except (httpx.NetworkError, ConnectionError, httpx.RemoteProtocolError, json.decoder.JSONDecodeError) as error:
      return (error, None)
    except Exception as e:
      return (str(e), None)

def save_audio(synth, wav_file):
  tmp_path = tempfile.TemporaryDirectory().name + 'record.wav'
  synth.save_wav(wav_file, tmp_path)
  return tmp_path

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