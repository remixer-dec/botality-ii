from concurrent.futures import ThreadPoolExecutor
import asyncio
import os

try:
  from llama_cpp import Llama
except ImportError:
  Llama = False

#TODO: model-name based assistant detection
assistant_mode = True
model = None

def init(model_paths, init_config={}):
  global model
  if not Llama:
    return print('llama.cpp is not installed, run "pip install llama-cpp-python" to install it')
  override = init_config['llama_cpp_init'] if 'llama_cpp_init' in init_config else {}
  lora_path = model_paths['path_to_llama_cpp_lora'] if 'path_to_llama_cpp_lora' in model_paths else None
  model = Llama(
    n_ctx=init_config.get('context_size', 512),
    model_path=model_paths["path_to_llama_cpp_weights"],
    seed=0,
    lora_path=lora_path,
    **override  
  )
  return {'instance': model, 'filename': os.path.basename(model_paths['path_to_llama_cpp_weights'])}

async def generate(prompt, length=64, model_params={}, assist=True):
  with ThreadPoolExecutor():
    if 'repetition_penalty' in model_params:
      model_params['repeat_penalty'] = model_params['repetition_penalty']
      del model_params['repetition_penalty']
    if 'early_stopping' in model_params:
      del model_params['early_stopping']
    output = await asyncio.to_thread(
      model, 
      prompt=prompt,
      stop=["</s>"],
      max_tokens=length,
       **model_params
    )
  return prompt + output['choices'][0]['text']