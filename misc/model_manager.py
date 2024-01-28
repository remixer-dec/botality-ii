import os
import sys
import json
import threading
import pathlib
from config_reader import config
from logging import Logger
from contextlib import contextmanager

try:
  from huggingface_hub import hf_hub_download
except ImportError:
  hf_hub_download = None

logger = Logger('model_manager')
bg_id = 0
bg_cache = {}

def transfer_kvs(source, allowed_keys, default_values):
  transferred = {}
  defaults = dict(enumerate(default_values))
  for index, key in enumerate(allowed_keys):
    value = source.get(key, defaults.get(index, None))
    if value is not None:
      transferred[key] = value
  return transferred

def get_models():
  models = {'TTS': {}}
  models['TTS']['SO_VITS_SVC'] = []
  for model in config.tts_so_vits_svc_voices:
    if os.path.exists(model.get('path', False)):
      models['TTS']['SO_VITS_SVC'].append({
        **transfer_kvs(model, ['voice', 'weights', 'author', 'repo', 'path'], []),
        "size": round(os.path.getsize(os.path.join(model.get('path'), model.get("weights"))) / 1024**3,3)
      })
  models['TTS']['VITS'] = []
  for v in config.tts_voices:
    if not isinstance(v, str):
      model = v
    else:
      model = {}
    path = os.path.join(model.get('path', config.tts_path), model.get('voice', v) + '.pth')
    if os.path.exists(path):
      models['TTS']['VITS'].append({
        **transfer_kvs(model, ['voice', 'model', 'path', 'author', 'repo'], [v, v, config.tts_path]),
        "size": round(os.path.getsize(path) / 1024**3,3)
      }) 
  models['LLM'] = {}
  models['LLM']['GGUF'] = []
  GGUF_DIR = config.llm_paths.get('path_to_llama_cpp_weights_dir', 'doesnotexist')
  if os.path.exists(GGUF_DIR):
    active_model = config.llm_paths.get('path_to_llama_cpp_weights')
    gguf_list = [x for x in os.listdir(GGUF_DIR) if x.lower().endswith('gguf')]
    models['LLM']['GGUF'] = [
      {
        'name': x,
        'model': x,
        'size': round(os.path.getsize(os.path.join(GGUF_DIR, x)) / 1024**3,3),
        'selected': os.path.samefile(os.path.join(GGUF_DIR, x), active_model) if os.path.exists(active_model) else False,
        'path': GGUF_DIR
      } for x in gguf_list]
  return models

def get_task_info(task_id):
  return bg_cache.get(task_id, {'status': 'not found'})

@contextmanager
def confirm(prompt):
  original_stdin = sys.stdin
  sys.stdin = open(0, closefd=False)
  user_answer = input(prompt)
  sys.stdin = original_stdin
  yield user_answer.lower() in ['y', 'yes']

def uninstall_model(model_type, model_config):
  return install_model(model_type, model_config, True)

def install_model(model_type, model_config, uninstall=False):
  if not hf_hub_download:
    return {"error": "Huggingface Hub library is not installed, please install it with $ pip install huggingface-hub"}
  if not uninstall:
    assert len(model_config.get('repo','').split('/')) == 2
  if model_type in supported_models:
    un = 'un' if uninstall else ''
    with confirm(f"Do you want to {un}install the {model_config.get('repo','')} {model_config.get('voice', model_config.get('name'))} {model_type} model? (Y/n): ") as confirmed:
      if confirmed:
        try:
          return supported_models[model_type][1 if uninstall else 0](model_config)
        except Exception as e:
          return {'error': str(e)}
    return {'error': 'Permission denied'}

def uninstall_gguf_model(model_config):
  GGUF_DIR = config.llm_paths.get('path_to_llama_cpp_weights_dir', None)
  if GGUF_DIR is None:
    return {'error': 'Please set up path_to_llama_cpp_weights_dir in llm_paths in your .env file'}
  else:
    if model_config.get('model') in os.listdir(GGUF_DIR):
      os.unlink(os.path.join(GGUF_DIR, model_config.get('model')))
      return {'response': 'ok'}
  return {'error': 'Unknown error'}

def install_gguf_model(model_config):
  global bg_id
  if '$path_to_llama_cpp_weights_dir' in model_config.get('installPath'):
    GGUF_DIR = config.llm_paths.get('path_to_llama_cpp_weights_dir', None)
    if GGUF_DIR is None:
      return {'error': 'Please set up path_to_llama_cpp_weights_dir in llm_paths in your .env file'}
    else:
      model_config['installPath'] = model_config['installPath'].replace('$path_to_llama_cpp_weights_dir', GGUF_DIR)
  dldir_path = model_config.get('installPath')
  model_name = model_config.get('model').replace('$', model_config.get('quant'))
  download_file_path = os.path.join(dldir_path, model_name)
  hf_file_path = model_config.get('path') + model_name
  if not os.path.exists(dldir_path):
    print('download dir does not exist, creating it', dldir_path)
    os.makedirs(dldir_path)
  if os.path.exists(download_file_path):
    return {'error': 'model already exists!'}
  bg_id = (bg_id + 1)
  bg_cache[bg_id] = {'status': 'running'}
  bg_thread = threading.Thread(target=install_gguf_model_bg, args=(model_config, hf_file_path, download_file_path, bg_id,))
  bg_thread.start()
  return {'response': {'status': 'running', 'task_id': bg_id}}

def install_gguf_model_bg(model_config, remote_file_path, local_file_path, task_id):
  try:
    download_and_move(model_config, remote_file_path, local_file_path)
  except Exception as e:
    logger.error(e)
    bg_cache[task_id] = {'status': 'error', 'error': str(e)}
    return
  bg_cache[task_id] = {'status': 'done'}

def install_tts_model(model_config):
  global bg_id
  download_file_path = model_config.get('path', '') + model_config.get('model')
  download_dir = model_config.get('installPath').replace('$TTS_PATH', config.tts_path)
  download_dir = download_dir + model_config.get('voice') if model_config.get('_type') == 'SO_VITS_SVC' else download_dir
  if not os.path.exists(download_dir):
    print('download dir does not exist, creating it', download_dir)
    os.makedirs(download_dir)
  config_path = os.path.join(download_dir, 'config.json')
  config_exists = os.path.exists(config_path)
  if not config_exists:
    print('downloading config to', config_path)
    download_and_move(model_config, os.path.join(model_config.get('path', ''), 'config.json'), config_path)
  model_path = os.path.join(download_dir, model_config.get('model') if not model_config.get('rename') else (model_config.get('voice') + '.pth'))
  if os.path.exists(model_path):
    return {'error': 'model is already installed'}
  else:
    bg_id = (bg_id + 1)
    bg_cache[bg_id] = {'status': 'running'}
    target_task = None
    if model_config.get('_type') == 'VITS':
      target_task = install_vits_background
    if model_config.get('_type') == 'SO_VITS_SVC':
      target_task = install_so_vits_svc_background
    
    bg_thread = threading.Thread(target=target_task, args=(model_config, download_file_path, model_path, bg_id,))
    bg_thread.start()
    return {'response': {'status': 'running', 'task_id': bg_id}}
  return "ok"

def uninstall_tts_model(model_config):
  model_config_dict = get_models()['TTS'][model_config.get('_type')]
  trusted_model_config = next((item for item in model_config_dict if (item if isinstance(item, str) else item.get('voice')) == model_config.get('voice')), None)
  trusted_model_config['_type'] = model_config.get('_type')
  model_config = trusted_model_config
  model_dir = model_config.get('path')
  filename = model_config.get('model') if model_config.get('_type') == 'SO_VITS_SVC' else (model_config.get('voice') + '.pth')
  full_path = os.path.join(model_dir, filename)
  print('deleting full_path', full_path)
  os.unlink(full_path)
  if model_config.get('_type') == 'SO_VITS_SVC':
    new_config = [x for x in config.tts_so_vits_svc_voices if x.get('voice') != model_config.get('voice')]
    config.tts_so_vits_svc_voices = new_config
  if model_config.get('_type') == 'VITS':
    new_config = [x for x in config.tts_voices if \
      (x if isinstance(x, str) else x.get('voice')) != model_config.get('voice')]
    config.tts_voices = new_config
  return {'response': 'ok'}
  

def download_and_move(model_config, remote_file_path, local_file_path):
  cached_file_path = hf_hub_download(repo_id=model_config.get('repo'), filename=remote_file_path)
  print('cached ', cached_file_path)
  to_unlink = []
  while os.path.islink(cached_file_path):
    to_unlink.append(cached_file_path)
    print('resolving symlink', cached_file_path)
    cached_file_path = pathlib.Path(cached_file_path).absolute().resolve()
  print('moving cached', cached_file_path, 'to', local_file_path)
  os.rename(cached_file_path, local_file_path)
  for file in to_unlink:
    print('removing symlinks')
    os.unlink(file)

def install_vits_background(model_config, remote_file_path, local_file_path, task_id):
  try:
    download_and_move(model_config, remote_file_path, local_file_path)
    del model_config['size']
    del model_config['model']
    del model_config['rename']
    del model_config['_type']
    model_config['path'] = os.path.dirname(local_file_path)
    del model_config['installPath']
    config.tts_voices.append(model_config)
    config.tts_voices = config.tts_voices
  except Exception as e:
    logger.error(e)
    bg_cache[task_id] = {'status': 'error', 'error': str(e)}
    return
  bg_cache[task_id] = {'status': 'done'}

def install_so_vits_svc_background(model_config, remote_file_path, local_file_path, task_id):
  try:
    download_and_move(model_config, remote_file_path, local_file_path)
    model_dir = os.path.dirname(local_file_path)
    del model_config['size']
    model_config['weights'] = model_config['model']
    model_config['base_voice'] = model_config['baseVoice']
    del model_config['model']
    del model_config['_type']
    del model_config['baseVoice']
    model_config['path'] = model_dir
    del model_config['installPath']
    with open(os.path.join(model_dir, 'config.json'), 'r+') as config_file:
      json_config = json.loads(config_file.read())
      model_config['v'] = '4.0' if json_config.get('model', {}).get('ssl_dim', 256) == 256 else '4.1'
      speaker = json_config.get('spk', {'Unknown': 0}).popitem()[0]
      if speaker != model_config.get('voice'):
        json_config['spk'] = {model_config.get('voice'): 0}
        print('changed speaker in config.json')
        config_file.seek(0)
        config_file.truncate()
        json.dump(config_file, indent=2)
    config.tts_so_vits_svc_voices.append(model_config)
    config.tts_so_vits_svc_voices = config.tts_so_vits_svc_voices
  except Exception as e:
    logger.error(e)
    bg_cache[task_id] = {'status': 'error', 'error': str(e)}
    return
  bg_cache[task_id] = {'status': 'done'}

def select_model(model_type, body):
  can_be_selected = {"GGUF": "path_to_llama_cpp_weights"}
  if model_type in can_be_selected:
    model_config_dict = get_models()['LLM'][model_type]
    for model in model_config_dict:
      if model['name'] == body.get('name'):
        config.llm_paths[can_be_selected[model_type]] = os.path.join(model['path'], model['name'])
        config.llm_paths = config.llm_paths
        return {'response': 'ok'}
    return {'error': 'model not found'}
  return {'error': 'model not supported'}

supported_models = {
  'VITS': (install_tts_model, uninstall_tts_model), 
  'SO_VITS_SVC': (install_tts_model, uninstall_tts_model),
  'GGUF': (install_gguf_model, uninstall_gguf_model),
}