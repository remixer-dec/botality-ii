import torch
import asyncio
import os
from concurrent.futures import ThreadPoolExecutor
from providers.llm.abstract_llm import AbstractLLM

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class AutoHF(AbstractLLM):
  def __init__(self, model_paths, init_config):
    from transformers import AutoTokenizer, AutoModelForCausalLM
    weights = model_paths['path_to_autohf_weights']
    self.tokenizer = AutoTokenizer.from_pretrained(weights)
    self.model = AutoModelForCausalLM.from_pretrained(weights)
    self.filename = os.path.basename(weights)

  def tokenize(self, prompt):
    encoded_prompt = self.tokenizer(prompt, return_tensors="pt").input_ids.to(device)
    return encoded_prompt

  async def generate(self, prompt, length=64, model_params={}, assist=False):
    error = None
    try:
      encoded_prompt = self.tokenize(prompt)
      if 'early_stopping' in model_params:
        del model_params['early_stopping']
      with ThreadPoolExecutor():
        output = await asyncio.to_thread(self.model.generate, 
          input_ids=encoded_prompt,
          no_repeat_ngram_size=2,
          max_new_tokens=length,
          early_stopping=True,
          do_sample=True,
          **model_params
        )
    except Exception as e:
      error = str(e)
    return (False, self.tokenizer.batch_decode(output, skip_special_tokens=True)[0]) if not error else (True, error)

init = AutoHF
