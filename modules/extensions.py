import logging
import os
import importlib
import traceback
from config_reader import config
logger = logging.getLogger(__name__)

class ExtensionsModule:
  def __init__(self, dp, bot):
    dp.extensions = {}
    if not (os.path.exists('extensions')):
      os.makedirs('extensions')
    extension_files = [f for f in os.listdir('extensions') if not f.startswith('_')]
    active_module_set = set(config.active_modules)
    try:
      for filename in extension_files:
        imported_extension = importlib.import_module('extensions.' + filename.replace('.py', ''))
        ext = imported_extension.extension
        if set(ext.dependencies).issubset(active_module_set):
          dp.extensions[ext.name] = ext(dp, bot)
    except Exception as e:
      logger.error(type(e).__name__ +  ': ' + str(e) + '\n' + traceback.format_exc())
