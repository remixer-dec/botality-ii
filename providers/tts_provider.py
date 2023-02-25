try:
  from TTS.utils.synthesizer import Synthesizer
except ImportError:
  Synthesizer = None
from config_reader import config
from pathlib import Path
import base64
import httpx
import json
import tempfile
import subprocess
import os

synthesizers = {}

async def tts(voice, text):
  try:
    for r in config.tts_replacements:
      text = text.replace(r, config.tts_replacements[r])
    if voice not in synthesizers:
      synthesizers[voice] = Synthesizer(
        tts_config_path=Path(config.tts_path) / "config.json",
        tts_checkpoint=Path(config.tts_path) / (voice + ".pth"),
        use_cuda=False,
      )
    data = synthesizers[voice].tts(text[:4096] + '.')
    return (True, save_audio(voice, data))
  except Exception as e:
    return (False, str(e))

async def remote_tts(voice, text):
  async with httpx.AsyncClient() as client:
    try:
      tts_payload = {"voice": voice, "text": text}
      response = await client.post(url=config.tts_host, json=tts_payload, timeout=None)
      r = response.json()
      if response.status_code == 200:
        response_data = response.json()
        error = response_data.get('error')
        if error:
          return (False, error)
        wpath =response_data.get("data")
        return (True, wpath)
      else:
        return (False, 'unknown error')
    except (httpx.NetworkError, ConnectionError, httpx.RemoteProtocolError, json.decoder.JSONDecodeError) as error:
      return (False, error)
    except Exception as e:
      return (False, str(e))

def save_audio(voice, wav_file):
  tmp_path = tempfile.TemporaryDirectory().name + 'record.wav'
  synthesizers[voice].save_wav(wav_file, tmp_path)
  return tmp_path

def tts_convert(wav_path):
  ogg_path = wav_path + '.ogg'
  subprocess.run([config.tts_ffmpeg_path, '-i', wav_path, '-acodec', 'libopus', '-b:a', '128k', '-vbr', 'off', ogg_path, '-y'])
  with open(ogg_path, 'rb') as f:
    data = f.read()  
  os.remove(wav_path)
  os.remove(ogg_path)
  return data