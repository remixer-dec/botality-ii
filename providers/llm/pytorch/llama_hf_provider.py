import os
import torch
from torch import mps
import asyncio
from concurrent.futures import ThreadPoolExecutor
from transformers import LlamaTokenizer, LlamaForCausalLM, GenerationConfig
from misc.mps_fixups import fixup_mps
from config_reader import config

tokenizer = None
model = None
submodel = None
assistant_mode = False
device = torch.device("cuda") if torch.cuda.is_available() \
          else torch.device("cpu") if not torch.backends.mps.is_available() \
          else torch.device('mps')

if torch.backends.mps.is_available() and config.apply_mps_fixes:
  fixup_mps()

def init(model_paths, init_config={}):
  global tokenizer, model, submodel, assistant_mode
  tokenizer = model_paths['path_to_hf_llama']
  weights = model_paths['path_to_hf_llama']
  tokenizer = LlamaTokenizer.from_pretrained(tokenizer)

  model = LlamaForCausalLM.from_pretrained(
    weights, 
    torch_dtype=torch.float16 if device is not torch.device('cpu') else torch.float32,
    device_map={"": device}
  )
  if 'path_to_llama_lora' in model_paths and os.path.exists(model_paths['path_to_llama_lora']):
    from peft import PeftModel
    submodel = PeftModel.from_pretrained(
      model,
      model_paths['path_to_llama_lora'],
      device_map={"": device},
      torch_dtype=torch.float16 if device is not torch.device('cpu') else torch.float32,
    )
    submodel.half()
    submodel.eval()
    assistant_mode = True

  model.config.bos_token_id = 1
  model.config.eos_token_id = 2
  tokenizer.pad_token = tokenizer.eos_token
  tokenizer.pad_token_id = tokenizer.eos_token_id

  model.half()
  model.eval()

def tokenize(prompt):
  encoded_prompt = tokenizer(prompt, return_tensors="pt").input_ids.to(device)
  return encoded_prompt

async def generate(prompt, length=64, model_params={}, use_submodel=False):
  encoded_prompt = tokenize(prompt)
  generation_config = GenerationConfig(
    num_beams=1,
    **model_params
  )
  used_model = submodel if use_submodel else model
  with ThreadPoolExecutor():
    with torch.no_grad():
      output = await asyncio.to_thread(used_model.generate, 
        input_ids=encoded_prompt,
        max_new_tokens=length,
        generation_config=generation_config,
        eos_token_id=used_model.config.eos_token_id,
        do_sample=True
      )
      output = tokenizer.batch_decode(output, skip_special_tokens=True)
  if torch.backends.mps.is_available():
    mps.empty_cache()
  elif torch.cuda.is_available():
    torch.cuda.empty_cache()
  return output[0]
