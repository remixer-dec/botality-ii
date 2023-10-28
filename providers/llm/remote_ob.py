import httpx 
import json
import logging
import asyncio
import subprocess
import psutil
from functools import partial
from misc.memory_manager import mload
from config_reader import config
from providers.llm.abstract_llm import AbstractLLM
from time import sleep

logger = logging.getLogger(__name__)
llm_host = config.llm_host
llm_load_started = False

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
          return 'Connection error', None
      except (httpx.NetworkError, ConnectionError, httpx.RemoteProtocolError, json.decoder.JSONDecodeError) as error:
        return str(error), None
      except Exception:
        return 'Unknown error', None

  def __init__(self, model_paths, init_config):
    self.init_config = init_config
    if config.llm_remote_launch_process_automatically and \
    config.mm_preload_models_on_start:
      asyncio.run(self.run_llm_service())
    else:
      error, data = asyncio.run(self.remote_llm_api('GET', 'api/v1/model', {}))
      if error:
        logger.warn('Unable to get remote language model name: ' + str(error))
      self.model = None
      self.filename = data.get('result') if not error else 'Unknown model'

  async def generate(self, prompt, length=64, model_params={}, assist=True):
    if config.llm_remote_launch_process_automatically:
      await self.run_llm_service()
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
      return str(error), None

  async def run_llm_service(self):
    global llm_load_started, last_pid
    if llm_load_started:
      return
    llm_load_started = True
    service = mload('llm-remote_ob',  
      partial(subprocess.Popen, config.llm_remote_launch_command.split(' '), cwd=config.llm_remote_launch_dir),
      lambda p: p.terminate(),
      lambda p: psutil.Process(p.pid).memory_info().rss, 
      gpu=True
    )
    if service.pid != last_pid:
      await asyncio.sleep(config.llm_remote_launch_waittime)
      await self.remote_llm_api('POST', 'api/v1/model', {'action': 'load', 'model_name': config.llm_remote_model_name}),
      self.model = None
      self.filename = config.llm_remote_model_name
    llm_load_started=False
    last_pid = service.pid
    return service

init = RemoteLLM
last_pid = -1 