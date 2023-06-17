import httpx 
import json
import logging
import asyncio
from config_reader import config
from providers.llm.abstract_llm import AbstractLLM

logger = logging.getLogger(__name__)
llm_host = config.llm_host

class RemoteLLM(AbstractLLM):
  assistant_mode = True
  async def remote_llm_api(self, method, endpoint, payload):
    async with httpx.AsyncClient() as client:
      try:
        if method == 'GET':
          response = await client.get(url=f'{llm_host}/{endpoint}', params=payload, timeout=None)
        else:
          response = await client.post(url=f'{llm_host}/{endpoint}', json=payload, timeout=None)
        if response.status_code == 200:
          response_data = response.json()
          return (False, response_data)
        else:
          return (True, 'Connection error')
      except (httpx.NetworkError, ConnectionError, httpx.RemoteProtocolError, json.decoder.JSONDecodeError) as error:
        return (True, str(error))
      except Exception:
        return (True, 'Unknown error')

  def __init__(self, model_paths, init_config={}):
    error, data = asyncio.run(self.remote_llm_api('GET', 'api/v1/model', {}))
    if error:
      logger.warn('Unable to get remote language model name: ' + str(data))
    self.model = None
    self.filename = data.get('result') if not error else 'Unknown model'

  async def generate(self, prompt, length=64, model_params={}, assist=True):
    data = {
      'prompt': prompt,
      'max_length': length,
      **model_params,
    }
    error, response = await self.remote_llm_api('POST', 'api/v1/generate', data)
    if not error:
      response = response.get('results')[0].get('text')
      logger.info(response)
      return False, prompt + response
    else:
      return True, str(error)

init = RemoteLLM