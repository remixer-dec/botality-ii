import base64
import httpx 
import json
import random
import asyncio
import logging
import subprocess
import psutil
from collections import defaultdict
from config_reader import config
from misc.memory_manager import mload
from functools import partial


logger = logging.getLogger(__name__)
request_payload = {
  "denoising_strength": 1,
  "prompt": "",
  "sampler_name": config.sd_default_sampler,
  "steps": config.sd_default_tti_steps,
  "cfg_scale": 5,
  "width": config.sd_default_width,
  "height": config.sd_default_height,
  "restore_faces": False,
  "tiling": False,
  "batch_size": 1,
  "n_iter": config.sd_default_n_iter,
  "negative_prompt": "",
  "eta": 71337
}

# hash: name
models = defaultdict(lambda: 'Unknown model')
embeddings = []
loras = []

sd_url = config.sd_host or "http://127.0.0.1:7860"

sd_service = False
sd_started = False

def run_sd_service():
  global sd_started
  if not config.sd_launch_process_automatically:
    return
  p = partial(subprocess.Popen, config.sd_launch_command.split(' '), cwd=config.sd_launch_dir, stderr=subprocess.DEVNULL)
  service = mload('sd-remote', 
    p, 
    lambda p: p.terminate() or (sd_started:=False),
    lambda p: psutil.Process(p.pid).memory_info().rss, 
    gpu=True
  )
  return service

def check_server(async_func):
  async def decorated_function(*args, **kwargs):
    global sd_service, sd_started
    if not config.sd_launch_process_automatically:
      return await async_func(*args, **kwargs)
    url = f"{sd_url}/sdapi/v1/sd-models"
    try:
      async with httpx.AsyncClient() as client:
        await client.get(url)
    except (httpx.HTTPError, httpx.NetworkError, ConnectionError, httpx.RemoteProtocolError):
      print("SD server is down. Restarting it...")
      if not sd_started or sd_service.poll() is not None:
        sd_service = run_sd_service()
        sd_started = True
        # better idea is to read stdout and wait for server, but it doesn't work for some reason
        await asyncio.sleep(config.sd_launch_waittime)
      else:
        # TODO: fix this mess sometime later
        sd_service = run_sd_service()
      return await async_func(*args, **kwargs)
    sd_service = run_sd_service()
    return await async_func(*args, **kwargs)
  return decorated_function

@check_server
async def refresh_model_list():
  global models, embeddings, loras
  try:
    async with httpx.AsyncClient() as client:
      model_response = await client.get(url=f'{sd_url}/sdapi/v1/sd-models',headers={'accept': 'application/json'}, timeout=None)
      embed_response = await client.get(url=f'{sd_url}/sdapi/v1/embeddings',headers={'accept': 'application/json'}, timeout=None)
      lora_response  = await client.get(url=f'{sd_url}/sdapi/v1/loras',headers={'accept': 'application/json'}, timeout=None)
      if model_response.status_code == 200 and embed_response.status_code == 200 and lora_response.status_code == 200: 
        model_response_data = model_response.json()
        embed_response_data = embed_response.json()
        lora_response_data  = lora_response.json()
        models.clear()
        embeddings.clear()
        loras.clear()
        for m in model_response_data:
          models[m['hash']] = m['model_name']
        for e in embed_response_data['loaded']:
          embeddings.append(e)
        for lora in lora_response_data:
          loras.append(lora['name'])
        loras[:] = [key for key in loras if key not in config.sd_lora_custom_activations]
      else:
        raise Exception('Server error')
  except Exception as e:
    logger.warn('Failed to load stable diffusion model names: ' + str(e))


def b642img(base64_image):
  return base64.b64decode(base64_image)

@check_server
async def switch_model(name):
  async with httpx.AsyncClient() as client:
    try:
      payload = {'sd_model_checkpoint': name}
      response = await client.post(url=f'{sd_url}/sdapi/v1/options', json=payload, timeout=None)
      if response.status_code == 200:
        return True
    except Exception:
      return False
  return False

@check_server
async def sd_get_images(payload, endpoint):
  if len(models.values()) == 0:
    await refresh_model_list()
  async with httpx.AsyncClient() as client:
    try:
      response = await client.post(url=f'{sd_url}/{endpoint}', json=payload, timeout=None)
      if response.status_code == 200:
        response_data = response.json()
        images = response_data.get("images")
        bstr_images = [b642img(i) for i in images]
        gen_info = json.loads(response_data.get('info'))
        gen_info['model'] = models[gen_info['sd_model_hash']]
        return (False, bstr_images, gen_info)
      else:
        return ('Connection error', None, None)
    except (httpx.NetworkError, ConnectionError, httpx.RemoteProtocolError, json.decoder.JSONDecodeError) as error:
      return (error, None, None)
    except Exception:
      return ('unknown error', None, None)


async def tti(override=None):
  payload = request_payload
  default_scale = config.sd_default_tti_cfg_scale
  payload['cfg_scale'] = random.choice([3,4,5,6]) if default_scale == 0 else default_scale
  if override:
    payload = {**payload, **override}
  return await sd_get_images(payload, 'sdapi/v1/txt2img')


async def iti(override=None):
  payload = request_payload
  payload['denoising_strength'] = config.sd_default_iti_denoising_strength
  payload['cfg_scale'] = config.sd_default_iti_cfg_scale
  payload['steps'] = config.sd_default_iti_steps
  payload['sampler_name'] = config.sd_default_iti_sampler
  if override:
    payload = {**payload, **override}
  return await sd_get_images(payload, 'sdapi/v1/img2img')
