from providers.tts.abstract_tts import AbstractTTS
from config_reader import config
import httpx
import tempfile
import json

class RemoteTTS(AbstractTTS):
  def __init__(self):
    self.is_available = config.tts_mode != 'local'
    self.name = 'remote'
    self.voices = []
    self.authors = []
    self.voice_metamap = {}
    self.system = False
  
  async def speak(self, voice, text):
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