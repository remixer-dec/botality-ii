import os
import sys
import torch
from concurrent.futures import ThreadPoolExecutor
from utils import b64_to_img
from providers.llm.abstract_llm import AbstractLLM
import asyncio
import inspect

#python3.10 -m torch.distributed.launch --use_env bot.py

class LlamaOrig(AbstractLLM):
  generator = None
  assistant_mode = False
  visual_mode = False
  def __init__(self, model_paths, init_config={}):
    llama_weights = model_paths['path_to_llama_weights']
    llama_tokenizer = model_paths['path_to_llama_tokenizer']
    sys.path.append(model_paths['path_to_llama_code'])
    self.filename = os.path.basename(llama_weights)
    if os.path.exists(model_paths.get('path_to_llama_multimodal_adapter', '')):
      self._load_multimodal_adapter(model_paths, llama_weights, llama_tokenizer)
    else:
      self._load_llama_model(model_paths, llama_weights, llama_tokenizer)

  def _load_llama_model(self, model_paths, llama_weights, llama_tokenizer):
    from example import setup_model_parallel, load
    with torch.inference_mode(mode=True):
      local_rank, world_size = setup_model_parallel()
      if 'adapter_path' in inspect.signature(load).parameters and \
         'path_to_llama_adapter' in model_paths and \
          os.path.exists(model_paths.get('path_to_llama_adapter', None)): 
        self.model = load(
          llama_weights, llama_tokenizer, model_paths['path_to_llama_adapter'], local_rank, world_size, 1024, 1
        )
        self.assistant_mode = True
      else:
        self.model = load(
          llama_weights, llama_tokenizer, local_rank, world_size, 1024, 1
        )

  def _load_multimodal_adapter(self, model_paths, llama_weights, llama_tokenizer):
    global generator, assistant_mode, visual_mode
    import llama
    device = 'mps' if torch.backends.mps.is_available() else ('cuda' if torch.cuda.is_available else 'cpu')
    lpath = os.path.dirname(llama_tokenizer)
    orig_generator, preprocess = llama.load(model_paths['path_to_llama_multimodal_adapter'], lpath, device)
    self.assistant_mode = True
    self.visual_mode = True
    class Wrapped_generator():
      def generate(self, prompt, use_adapter=True, visual_input=False, **kwargs):
        if visual_input:
          img = b64_to_img(visual_input)
          img = preprocess(img).unsqueeze(0).half().to(device)
        else:
          img = []
        generated = orig_generator.generate(img, prompt, **kwargs)
        return [prompt[0] + generated[0]]
    self.model = Wrapped_generator()

  async def generate(self, prompt, max_gen_len=64, params={}, assist=False):
    available_params = inspect.signature(self.model.generate).parameters
    for param in list(params):
      if param not in available_params:
        del params[param]
    error = None
    with ThreadPoolExecutor():
      if self.assistant_mode and 'use_adapter' in available_params:
        params['use_adapter'] = assist
      try:
        results = await asyncio.to_thread(self.model.generate,
          [prompt], max_gen_len=max_gen_len, **params
        )
      except Exception as e:
        error = str(e)
    return (False, results[0]) if not error else (True, error)

init = LlamaOrig