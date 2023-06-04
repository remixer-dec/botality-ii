from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from config_reader import config
import asyncio
import os

try:
  from llama_cpp import Llama
except ImportError:
  Llama = False

assistant_mode = True
model = None

def init(model_paths, init_config={}):
  global model
  if not Llama:
    print('llama.cpp is not installed, run "pip install llama-cpp-python" to install it')
    return print('for GPU support, please read https://github.com/abetlen/llama-cpp-python')
  override = init_config['llama_cpp_init'] if 'llama_cpp_init' in init_config else {}
  lora_path = model_paths['path_to_llama_cpp_lora'] if 'path_to_llama_cpp_lora' in model_paths else None
  model = Llama(
    n_ctx=min(init_config.get('context_size', 512), config.llm_lcpp_max_context_size),
    n_gpu_layers=config.llm_lcpp_gpu_layers,
    model_path=model_paths["path_to_llama_cpp_weights"],
    seed=0,
    lora_path=lora_path,
    **override  
  )
  return {'instance': model, 'filename': os.path.basename(model_paths['path_to_llama_cpp_weights'])}

async def generate(prompt, length=64, model_params={}, assist=True):
  if 'repetition_penalty' in model_params:
    model_params['repeat_penalty'] = model_params['repetition_penalty']
    del model_params['repetition_penalty']
  if 'early_stopping' in model_params:
    del model_params['early_stopping']
  with ThreadPoolExecutor():
    output = await asyncio.to_thread(
      model, 
      prompt=prompt,
      stop=["</s>"],
      max_tokens=length,
       **model_params
    )
  return prompt + output['choices'][0]['text']

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
