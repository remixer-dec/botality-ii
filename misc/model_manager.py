import os
import sys
import json
import threading
import pathlib
from config_reader import config
from logging import Logger
try:
  from huggingface_hub import hf_hub_download
except ImportError:
  hf_hub_download = None

logger = Logger('model_manager')
bg_id = 0
bg_cache = {}

def get_models():
  models = {'TTS': {}}
  models['TTS']['SO_VITS_SVC'] = []
  for model in config.tts_so_vits_svc_voices:
    if os.path.exists(model.get('path', False)):
      models['TTS']['SO_VITS_SVC'].append({
        "voice": model.get('voice'),
        "model": model.get('weights'),
        "author": model.get('author'),
        "repo": model.get('repo'),
        "path": model.get('path'),
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
        "voice": model.get('voice', v),
        "model": model.get('model', v),
        "path":  model.get('path', config.tts_path),
        "author": model.get('author'),
        "repo": model.get('repo'),
        "size": round(os.path.getsize(path) / 1024**3,3)
      }) 
  return models

def get_task_info(task_id):
  return bg_cache.get(task_id, {'status': 'not found'})

def install_model(model_type, model_config):
  if not hf_hub_download:
    return {"error": "Huggingface Hub library is not installed, please install it with $ pip install huggingface-hub"}
  assert len(model_config.get('repo','').split('/')) == 2
  if model_type in supported_models:
    original_stdin = sys.stdin
    sys.stdin = open(0, closefd=False)
    user_answer = input(f"Do you want to install the {model_config.get('repo')} {model_type} model? (Y/n): ")
    if user_answer.lower() in ['y', 'yes']:
      try:
        return supported_models[model_type](model_config)
      except Exception as e:
        return {'error': str(e)}
    sys.stdin = original_stdin
    return {'error': 'Permission denied'}

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
    print(config.tts_voices)
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

supported_models = {'VITS': install_tts_model, 'SO_VITS_SVC': install_tts_model}