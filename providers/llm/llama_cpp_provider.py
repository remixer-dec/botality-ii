from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from config_reader import config
from providers.llm.abstract_llm import AbstractLLM
import asyncio
import os
import logging

logger = logging.getLogger(__name__)

try:
  from llama_cpp import Llama
except ImportError:
  Llama = False

class LlamaCPP(AbstractLLM):
  assistant_mode = True
  def __init__(self, model_paths, init_config={}):
    if not Llama:
      logger.error('llama.cpp is not installed, run "pip install llama-cpp-python" to install it')
      return logger.error('for GPU support, please read https://github.com/abetlen/llama-cpp-python')
    override = init_config.get('llama_cpp_init', {})
    lora_path = model_paths.get('path_to_llama_cpp_lora', None)
    self.model = Llama(
      n_ctx=min(init_config.get('context_size', 512), config.llm_lcpp_max_context_size),
      rope_freq_base=init_config.get('rope_freq_base', 10000),
      rope_freq_scale=init_config.get('rope_freq_scale', 1.0),
      n_gpu_layers=config.llm_lcpp_gpu_layers,
      model_path=model_paths["path_to_llama_cpp_weights"],
      seed=0,
      lora_path=lora_path,
      **override  
    )
    self.filename = os.path.basename(model_paths['path_to_llama_cpp_weights'])
    
  async def generate(self, prompt, length=64, model_params={}, assist=True):
    if 'repetition_penalty' in model_params:
      model_params['repeat_penalty'] = model_params['repetition_penalty']
      del model_params['repetition_penalty']
    if 'early_stopping' in model_params:
      del model_params['early_stopping']
    output = error = None
    with ThreadPoolExecutor():
      try:
        output = await asyncio.to_thread(
          self.model, 
          prompt=prompt,
          stop=["</s>"],
          max_tokens=length,
           **model_params
        )
      except Exception as e:
        error = str(e)
    if not error:
      output = output['choices'][0]['text']
      logger.info(output)
      output = prompt + output
    return (False, output) if not error else (True, error)

## process-based approach re-creates a new process and re-allocates memory on every run
## which is not optimal, I leave this code for future reference
# import functools
# async def generate_mp(prompt, length=64, model_params={}, assist=True):
#   with ProcessPoolExecutor(max_workers=1) as executor:
#     loop = asyncio.get_event_loop()
#     binded = functools.partial(
#       model, 
#      prompt=prompt,
#       stop=["</s>"],
#       max_tokens=length,
#        **model_params
#     )
#     output = loop.run_in_executor(executor, binded)
#     output = await output
#     return prompt + output['choices'][0]['text']
init = LlamaCPP