import logging
import os
import importlib
import traceback
from config_reader import config
logger = logging.getLogger(__name__)

class ExtensionsModule:
  def __init__(self, dp, bot):
    dp.extensions = {}
    self.dir = 'extensions'
    if not (os.path.exists(self.dir)):
      os.makedirs(self.dir)
    self.load_from_dir(self.dir, dp, bot)
  
  def load_from_dir(self, exdir, dp, bot):
    extension_files = [f for f in os.listdir(exdir) if not f.startswith('_') and f.endswith('.py')]
    extension_dirs = [f for f in os.listdir(exdir) if os.path.isdir(os.path.join(exdir, f))]
    for dir in extension_dirs:
      dir_ext_path = os.path.join(dir, 'extension.py')
      if os.path.exists(os.path.join(exdir, dir_ext_path)):
        extension_files.append(dir_ext_path)
    
    active_module_set = set(config.active_modules)
    for filename in extension_files:
      try:
        logger.info("loading extension: " + filename)
        imported_extension = importlib.import_module(exdir + '.' + filename.replace(os.path.sep, '.').replace('.py', ''))
        assert hasattr(imported_extension, "extension"), "Extension must have 'extension' variable"
        assert hasattr(imported_extension.extension, "name"), "Extension must have a name"
        ext = imported_extension.extension
        if set(ext.dependencies).issubset(active_module_set):
          dp.extensions[ext.name] = ext(dp, bot)
      except Exception as e:
        logger.error(f"error loading extension {filename}\n{type(e).__name__}:{str(e)}\n{traceback.format_exc()}")
