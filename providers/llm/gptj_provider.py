import numpy as np
import torch
from concurrent.futures import ThreadPoolExecutor
import asyncio

tokenizer = None
model = None
device = torch.device("cpu")


def init(model_paths, init_config={}):
  global tokenizer, model
  from transformers import AutoTokenizer, GPTJForCausalLM
  weights = model_paths['path_to_gptj_weights']
  tokenizer = AutoTokenizer.from_pretrained(weights)
  model = GPTJForCausalLM.from_pretrained(weights, revision="float16", torch_dtype=torch.float32, low_cpu_mem_usage=True)
  model = model.to(device)

def tokenize(prompt):
  encoded_prompt = tokenizer(prompt, return_tensors="pt").input_ids.to(device)
  return encoded_prompt

async def generate(prompt, length=64, model_params={}, assist=False):
  encoded_prompt = tokenize(prompt)
  with ThreadPoolExecutor():
    output = await asyncio.to_thread(model.generate, 
      input_ids=encoded_prompt,
      max_length=len(encoded_prompt[0]) + length,
      do_sample=True,
      **model_params
    )
  return tokenizer.batch_decode(output)[0]
