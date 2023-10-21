import torch
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace
from providers.llm.abstract_llm import AbstractLLM

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class GPT2(AbstractLLM):
  is_nanoGPT = False
  assistant_mode = False
  def __init__(self, model_paths, init_config):
    from transformers import GPT2LMHeadModel, GPT2Tokenizer
    weights = model_paths['path_to_gpt2_weights']
    self.filename = os.path.basename(weights)
    if 'use_tiktoken' in init_config and init_config['use_tiktoken']:
      import tiktoken
      tk = tiktoken.get_encoding("gpt2")
      tokenizer = {}
      tokenizer["encode"] = lambda s, *args, **kwargs: torch.tensor(tk.encode(s, allowed_special={"<|endoftext|>"}), dtype=torch.long, device=device)[None, ...]
      tokenizer["decode"] = lambda l: tk.decode(l.tolist())
      tokenizer["name"] = 'tiktoken'
      tokenizer = SimpleNamespace(**tokenizer)
      self.tokenizer = tokenizer
    else:
      self.tokenizer = GPT2Tokenizer.from_pretrained(weights)
    if 'nanogpt' in init_config and init_config['nanogpt']:
      import sys
      sys.path.append(model_paths['path_to_minchatgpt_code'])
      from gpt import GPT
      from configs import get_configs
      self.is_nanoGPT = True
      cfg = get_configs("gpt2-medium")
      model = GPT(cfg)
      model.load_state_dict(state_dict=torch.load(weights), strict=False)
      self.assistant_mode = True
    else:
      model = GPT2LMHeadModel.from_pretrained(weights)
    self.model = model.to(device)

  def tokenize(self, prompt):
    encoded_prompt = self.tokenizer.encode(prompt, add_special_tokens=False, return_tensors="pt")
    encoded_prompt = encoded_prompt.to(device)
    return encoded_prompt[:, :1024]

  async def generate(self, prompt, length=64, model_params={}, assist=False):
    error = None
    try:
      encoded_prompt = self.tokenize(prompt)
      with ThreadPoolExecutor():
        if not self.is_nanoGPT:
          output_sequences = await asyncio.to_thread(self.model.generate, 
            input_ids=encoded_prompt,
            max_length=length + len(encoded_prompt[0]),
            do_sample=True,
            num_return_sequences=1,
            **model_params
          )
        else:
          if 'early_stopping' in model_params:
            del model_params['early_stopping']
          output_sequences = await asyncio.to_thread(self.model.generate, 
            encoded_prompt,
            length,
            **model_params
          )
    except Exception as e:
      error = str(e)
    return (False, self.tokenizer.decode(output_sequences[0])) if not error else (True, error)

init = GPT2