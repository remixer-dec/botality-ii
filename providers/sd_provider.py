import base64
import httpx 
import json
import random
import asyncio
from collections import defaultdict
from config_reader import config

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

sd_url = config.sd_host or "http://127.0.0.1:7860"

async def refresh_model_list():
  global models, embeddings
  try:
    async with httpx.AsyncClient() as client:
      model_response = await client.get(url=f'{sd_url}/sdapi/v1/sd-models',headers={'accept': 'application/json'}, timeout=None)
      embed_response = await client.get(url=f'{sd_url}/sdapi/v1/embeddings',headers={'accept': 'application/json'}, timeout=None)
      if model_response.status_code == 200 and embed_response.status_code == 200: 
        model_response_data = model_response.json()
        embed_response_data = embed_response.json()
        models = defaultdict(lambda: 'Unknown model')
        embeddings = []
        for m in model_response_data:
          models[m['hash']] = m['model_name']
        for e in embed_response_data['loaded']:
          embeddings.append(e)
      else:
        raise Exception('Server error')
  except Exception as e:
    print('Failed to load model names:' + str(e))

def b642img(base64_image):
  return base64.b64decode(base64_image)

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



async def sd_get_images(payload, endpoint):
  async with httpx.AsyncClient() as client:
    try:
      response = await client.post(url=f'{sd_url}/{endpoint}', json=payload, timeout=None)
      if response.status_code == 200:
        response_data = response.json()
        images = response_data.get("images")
        bstr_images = [b642img(i) for i in images]
        gen_info = json.loads(response_data.get('info'))
        gen_info['model'] = models[gen_info['sd_model_hash']]
        return (True, bstr_images, gen_info)
      else:
        return (False, r['detail'], None)
    except (httpx.NetworkError, ConnectionError, httpx.RemoteProtocolError, json.decoder.JSONDecodeError) as error:
      return (False, error, None)
    except Exception:
      return (False, 'unknown error', None)


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
  if override:
    payload = {**payload, **override}
  return await sd_get_images(payload, 'sdapi/v1/img2img')



asyncio.run(refresh_model_list())