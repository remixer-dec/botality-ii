from utils import cprint
try:
  import torch
  from TTS.utils.synthesizer import Synthesizer
except ImportError:
  Synthesizer = None
  cprint("TTS module not available, please reinstall it", color="red")
from config_reader import config
from pathlib import Path
import httpx
import json
import tempfile
import subprocess
import os
import time
from config_reader import config

synthesizers = {}
so_vits_svc_voices = dict({m['voice'].lower().replace('-',''): m for m in config.tts_so_vits_svc_voices})

async def so_vits_svc(voice, text, original_audio=False):
  so_vits_svc_code = config.tts_so_vits_svc_code_path
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
    ["python", f"inference_main.py", "-m", str(so_vits_model), "-c", str(so_vits_config), 
    "-n", f'{name}.wav', "-t", "0", "-s", so_vits_voice]
    ,
    cwd=so_vits_svc_code
  )
  os.remove(temp_file)
  os.remove(temp_file_wav)
  return (False, f'{so_vits_svc_code}/results/{name}.wav_0key_{so_vits_voice}.flac')

async def tts(voice, text):
  try:
    assert os.path.exists(config.tts_ffmpeg_path)
    for r in config.tts_replacements:
      text = text.replace(r, config.tts_replacements[r])
    if voice in so_vits_svc_voices:
      return await so_vits_svc(voice, text)
    if voice not in synthesizers:
      synthesizers[voice] = Synthesizer(
        tts_config_path=Path(config.tts_path) / "config.json",
        tts_checkpoint=Path(config.tts_path) / (voice + ".pth"),
        use_cuda=torch.cuda.is_available(),
      )
    data = synthesizers[voice].tts(text[:4096] + '.')
    return (False, save_audio(voice, data))
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

def save_audio(voice, wav_file):
  tmp_path = tempfile.TemporaryDirectory().name + 'record.wav'
  synthesizers[voice].save_wav(wav_file, tmp_path)
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