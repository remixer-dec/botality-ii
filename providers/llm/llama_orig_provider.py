import os
import sys
import torch
from concurrent.futures import ThreadPoolExecutor
import asyncio
import inspect

generator = None
assistant_mode = False
#python3.10 -m torch.distributed.launch --use_env bot.py

def init(model_paths, init_config={}):
  global generator, assistant_mode
  llama_weights = model_paths['path_to_llama_weights']
  llama_tokenizer = model_paths['path_to_llama_tokenizer']
  sys.path.append(model_paths['path_to_llama_code'])
  from example import setup_model_parallel, load
  with torch.inference_mode(mode=True):
    local_rank, world_size = setup_model_parallel()
    if "adapter_path" in inspect.signature(load).parameters and \
       'path_to_llama_adapter' in model_paths and \
        os.path.exists(model_paths['path_to_llama_adapter']): 
      generator = load(
        llama_weights, llama_tokenizer, model_paths['path_to_llama_adapter'], local_rank, world_size, 1024, 1
      )
      assistant_mode = True
    else:
      generator = load(
        llama_weights, llama_tokenizer, local_rank, world_size, 1024, 1
      )

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