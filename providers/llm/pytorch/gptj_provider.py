import torch
import asyncio
import os
from concurrent.futures import ThreadPoolExecutor
from providers.llm.abstract_llm import AbstractLLM

tokenizer = None
model = None
device = torch.device("cpu")

class GPTJ(AbstractLLM):
  def __init__(self, model_paths, init_config):
    from transformers import AutoTokenizer, GPTJForCausalLM
    weights = model_paths['path_to_gptj_weights']
    self.tokenizer = AutoTokenizer.from_pretrained(weights)
    self.model = GPTJForCausalLM.from_pretrained(weights, revision="float16", torch_dtype=torch.float32, low_cpu_mem_usage=True)
    self.model = self.model.to(device)
    self.filename = os.path.basename(weights)

  def tokenize(self, prompt):
    encoded_prompt = self.tokenizer(prompt, return_tensors="pt").input_ids.to(device)
    return encoded_prompt

  async def generate(self, prompt, length=64, model_params={}, assist=False):
    encoded_prompt = self.tokenize(prompt)
    error = None
    try:
      with ThreadPoolExecutor():
        output = await asyncio.to_thread(self.model.generate, 
          input_ids=encoded_prompt,
          max_length=len(encoded_prompt[0]) + length,
          do_sample=True,
          **model_params
        )
    except Exception as e:
      error = str(e)
    return (False, self.tokenizer.batch_decode(output)[0]) if not error else (True, error)

init = GPTJ
