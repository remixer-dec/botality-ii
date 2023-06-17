import os
import torch
from torch import mps
import asyncio
from concurrent.futures import ThreadPoolExecutor
from transformers import LlamaTokenizer, LlamaForCausalLM, GenerationConfig
from misc.mps_fixups import fixup_mps
from config_reader import config
from providers.llm.abstract_llm import AbstractLLM

device = torch.device("cuda") if torch.cuda.is_available() \
  else torch.device("cpu") if not torch.backends.mps.is_available() \
  else torch.device('mps')

if torch.backends.mps.is_available() and config.apply_mps_fixes:
  fixup_mps()

class LlamaHuggingface(AbstractLLM):
  submodel = None
  assistant_mode = False
  def __init__(self, model_paths, init_config={}):
    tokenizer = model_paths['path_to_hf_llama']
    weights = model_paths['path_to_hf_llama']
    self.tokenizer = LlamaTokenizer.from_pretrained(tokenizer)
    self.model = LlamaForCausalLM.from_pretrained(
      weights, 
      torch_dtype=torch.float16 if device is not torch.device('cpu') else torch.float32,
      device_map={"": device}
    )

    if os.path.exists(model_paths.get('path_to_llama_lora', '')):
      from peft import PeftModel
      self.submodel = PeftModel.from_pretrained(
        self.model,
        model_paths['path_to_llama_lora'],
        device_map={"": device},
        torch_dtype=torch.float16 if device is not torch.device('cpu') else torch.float32,
      )
      self.submodel.half()
      self.submodel.eval()
      self.assistant_mode = True

    self.model.config.bos_token_id = 1
    self.model.config.eos_token_id = 2
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.pad_token_id = tokenizer.eos_token_id

    self.model.half()
    self.model.eval()
    self.filename = os.path.basename(model_paths['path_to_hf_llama'])

  def tokenize(self, prompt):
    return self.tokenizer(prompt, return_tensors="pt").input_ids.to(device)

  async def generate(self, prompt, length=64, model_params={}, use_submodel=False):
    encoded_prompt = self.tokenize(prompt)
    generation_config = GenerationConfig(
      num_beams=1,
      **model_params
    )
    model = self.submodel if use_submodel else self.model
    error = None
    try:
      with ThreadPoolExecutor():
        with torch.no_grad():
          output = await asyncio.to_thread(model.generate, 
            input_ids=encoded_prompt,
            max_new_tokens=length,
            generation_config=generation_config,
            eos_token_id=model.config.eos_token_id,
            do_sample=True
          )
          output = self.tokenizer.batch_decode(output, skip_special_tokens=True)
      if torch.backends.mps.is_available():
        mps.empty_cache()
      elif torch.cuda.is_available():
        torch.cuda.empty_cache()
    except Exception as e:
      error = str(e)
    return (False, output[0]) if not error else (True, error)

init = LlamaHuggingface