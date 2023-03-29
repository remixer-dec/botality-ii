import torch
from concurrent.futures import ThreadPoolExecutor
import asyncio
from types import SimpleNamespace

tokenizer = None
model = None
is_nanoGPT = False
assistant_mode = False
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def init(model_paths, init_config={}):
  global model, tokenizer, is_nanoGPT, assistant_mode
  from transformers import GPT2LMHeadModel, GPT2Tokenizer
  weights = model_paths['path_to_gpt2_weights']
  if 'use_tiktoken' in init_config and init_config['use_tiktoken']:
    import tiktoken
    tk = tiktoken.get_encoding("gpt2")
    tokenizer = {}
    tokenizer["encode"] = lambda s, *args, **kwargs: torch.tensor(tk.encode(s, allowed_special={"<|endoftext|>"}), dtype=torch.long, device=device)[None, ...]
    tokenizer["decode"] = lambda l: tk.decode(l.tolist())
    tokenizer["name"] = 'tiktoken'
    tokenizer = SimpleNamespace(**tokenizer)
  else:
    tokenizer = GPT2Tokenizer.from_pretrained(weights)
  if 'nanogpt' in init_config and init_config['nanogpt']:
    import sys
    sys.path.append(model_paths['path_to_minchatgpt_code'])
    from gpt import GPT
    from configs import get_configs
    is_nanoGPT = True
    cfg = get_configs("gpt2-medium")
    model = GPT(cfg)
    model.load_state_dict(state_dict=torch.load(weights), strict=False)
    assistant_mode = True
  else:
    model = GPT2LMHeadModel.from_pretrained(weights)
  model = model.to(device)


def tokenize(prompt):
  encoded_prompt = tokenizer.encode(prompt, add_special_tokens=False, return_tensors="pt")
  encoded_prompt = encoded_prompt.to(device)
  return encoded_prompt[:, :1024]


async def generate(prompt, length=64, model_params={}, assist=False):
  encoded_prompt = tokenize(prompt)
  with ThreadPoolExecutor():
    if not is_nanoGPT:
      output_sequences = await asyncio.to_thread(model.generate, 
        input_ids=encoded_prompt,
        max_length=length + len(encoded_prompt[0]),
        do_sample=True,
        num_return_sequences=1,
        **model_params
      )
    else:
      if 'early_stopping' in model_params:
        del model_params['early_stopping']
      output_sequences = await asyncio.to_thread(model.generate, 
        encoded_prompt,
        length,
        **model_params
      )
  return tokenizer.decode(output_sequences[0])