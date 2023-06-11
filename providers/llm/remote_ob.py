import httpx 
import json
import logging
import asyncio
from config_reader import config

logger = logging.getLogger(__name__)
llm_host = config.llm_host
assistant_mode = True

async def remote_llm_api(method, endpoint, payload):
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
        return ('Connection error', None)
    except (httpx.NetworkError, ConnectionError, httpx.RemoteProtocolError, json.decoder.JSONDecodeError) as error:
      return (error, None)
    except Exception:
      return ('Unknown error', None)


def init(model_paths, init_config={}):
  error, model = asyncio.run(remote_llm_api('GET', 'api/v1/model', {}))
  if error:
    logger.warn('Unable to get remote language model name: ' + str(error))
  return {'instance': None, 'filename': model.get('result') if model else 'Unknown model'}

async def generate(prompt, length=64, model_params={}, assist=True):
  data = {
    'prompt': prompt,
    'max_length': length,
    **model_params,
  }
  print(data)
  error, response = await remote_llm_api('POST', 'api/v1/generate', data)
  if not error:
    return prompt + response.get('results')[0].get('text')
  else:
    # TODO: refactor error delivery
    return prompt + 'Error: ' + str(error) + '\n'

