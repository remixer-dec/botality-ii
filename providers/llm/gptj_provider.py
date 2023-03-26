import numpy as np
import torch

tokenizer = None
model = None
device = torch.device("cpu")


def init(model_path):
  global tokenizer, model
  from transformers import AutoTokenizer, GPTJForCausalLM
  tokenizer = AutoTokenizer.from_pretrained(model_path)
  model = GPTJForCausalLM.from_pretrained(model_path, revision="float16", torch_dtype=torch.float32, low_cpu_mem_usage=True)
  model = model.to(device)

def tokenize(prompt):
  encoded_prompt = tokenizer(prompt, return_tensors="pt").input_ids.to(device)
  return encoded_prompt

def generate(encoded_prompt, length=64, model_params={}):
  output = model.generate(
    input_ids=encoded_prompt,
    max_length=len(encoded_prompt[0]) + length,
    do_sample=True,
    **model_params
  )
  return tokenizer.batch_decode(output)[0]
