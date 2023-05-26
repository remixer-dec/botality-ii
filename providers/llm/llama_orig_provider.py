import os
import sys
import torch
from concurrent.futures import ThreadPoolExecutor
from utils import b64_to_img
import asyncio
import inspect

generator = None
assistant_mode = False
visual_mode = False
#python3.10 -m torch.distributed.launch --use_env bot.py

def load_llama_model(model_paths, llama_weights, llama_tokenizer):
  global generator, assistant_mode
  from example import setup_model_parallel, load
  with torch.inference_mode(mode=True):
    local_rank, world_size = setup_model_parallel()
    if "adapter_path" in inspect.signature(load).parameters and \
       'path_to_llama_adapter' in model_paths and \
        os.path.exists(model_paths.get('path_to_llama_adapter', None)): 
      generator = load(
        llama_weights, llama_tokenizer, model_paths['path_to_llama_adapter'], local_rank, world_size, 1024, 1
      )
      assistant_mode = True
    else:
      generator = load(
        llama_weights, llama_tokenizer, local_rank, world_size, 1024, 1
      )

def load_multimodal_adapter(model_paths, llama_weights, llama_tokenizer):
  global generator, assistant_mode, visual_mode
  import llama
  device = 'mps' if torch.backends.mps.is_available() else ('cuda' if torch.cuda.is_available else 'cpu')
  lpath = os.path.dirname(llama_tokenizer)
  orig_generator, preprocess = llama.load(model_paths['path_to_llama_multimodal_adapter'], lpath, device)
  assistant_mode = True
  visual_mode = True
  class Wrapped_generator():
    def generate(self, prompt, use_adapter=True, visual_input=False, **kwargs):
      if visual_input:
        img = b64_to_img(visual_input)
        img = preprocess(img).unsqueeze(0).half().to(device)
      else:
        img = []
      generated = orig_generator.generate(img, prompt, **kwargs)
      return [prompt[0] + generated[0]]
  generator = Wrapped_generator()

def init(model_paths, init_config={}):
  llama_weights = model_paths['path_to_llama_weights']
  llama_tokenizer = model_paths['path_to_llama_tokenizer']
  sys.path.append(model_paths['path_to_llama_code'])
  if os.path.exists(model_paths.get('path_to_llama_multimodal_adapter', '')):
    load_multimodal_adapter(model_paths, llama_weights, llama_tokenizer)
  else:
    load_llama_model(model_paths, llama_weights, llama_tokenizer)

def tokenize(prompt):
  return prompt

async def generate(prompt, max_gen_len=64, params={}, assist=False):
  available_params = inspect.signature(generator.generate).parameters
  for param in list(params):
    if param not in available_params:
      del params[param]
  with ThreadPoolExecutor():
    if assistant_mode and 'use_adapter' in available_params:
      params['use_adapter'] = assist
    results = await asyncio.to_thread(generator.generate,
      [prompt], max_gen_len=max_gen_len, **params
    )
  return results[0]