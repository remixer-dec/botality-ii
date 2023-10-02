import os
from config_reader import config

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
      