import os
import sys
import torch
from concurrent.futures import ThreadPoolExecutor
import asyncio

generator = None
#python3.10 -m torch.distributed.launch --use_env bot.py

def init(model_paths, init_config={}):
  global generator
  llama_weights = model_paths['path_to_llama_weights']
  llama_tokenizer = model_paths['path_to_llama_tokenizer']
  sys.path.append(model_paths['path_to_llama_code'])
  from example import setup_model_parallel, load
  with torch.inference_mode(mode=True):
    local_rank, world_size = setup_model_parallel()
    generator = load(
      llama_weights, llama_tokenizer, local_rank, world_size, 1024, 1
    )

def tokenize(prompt):
  return prompt

async def generate(prompt, max_gen_len=64, params={}, assist=False):
  if 'top_k' in params:
    del params['top_k']
  if 'repetition_penalty' in params:
    del params['repetition_penalty']
  with ThreadPoolExecutor():
    results = await asyncio.to_thread(generator.generate,
      [prompt], max_gen_len=max_gen_len, **params
    )
  return results[0]