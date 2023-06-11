import torch
from concurrent.futures import ThreadPoolExecutor
import asyncio

tokenizer = None
model = None
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def init(model_paths, init_config={}):
  global tokenizer, model
  from transformers import AutoTokenizer, AutoModelForCausalLM
  weights = model_paths['path_to_cerebras_weights']
  tokenizer = AutoTokenizer.from_pretrained(weights)
  model = AutoModelForCausalLM.from_pretrained(weights)


def tokenize(prompt):
  encoded_prompt = tokenizer(prompt, return_tensors="pt").input_ids.to(device)
  return encoded_prompt

async def generate(prompt, length=64, model_params={}, assist=False):
  encoded_prompt = tokenize(prompt)
  if 'early_stopping' in model_params:
    del model_params['early_stopping']
  with ThreadPoolExecutor():
    output = await asyncio.to_thread(model.generate, 
      input_ids=encoded_prompt,
      no_repeat_ngram_size=2,
      max_new_tokens=length,
      early_stopping=True,
      do_sample=True,
      **model_params
    )
  return tokenizer.batch_decode(output, skip_special_tokens=True)[0]
