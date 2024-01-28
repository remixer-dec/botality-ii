from abc import ABCMeta, abstractmethod
from collections import defaultdict
from config_reader import config
from pydantic import BaseModel
from typing import List

class BaseExtensionConfig(BaseModel):
  def __init__(self, name, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.__dict__['__name'] = name

  def __setattr__(self, key, value):
    config.extensions_config[self.__dict__['__name']][key] = value
    # trigger config setter to save changes in file
    config.extensions_config = config.extensions_config

class BaseExtension(metaclass=ABCMeta):
  name: str
  dependencies: List[str]

  def __init__(self, ext_config):
    saved_confg = config.extensions_config.get(self.name, {})
    self.config = ext_config(self.name, **saved_confg)
    if not saved_confg:
      config.extensions_config[self.name] = self.config.dict(exclude={'__name': True})
      # trigger config setter to save changes in file
      if config.extensions_config[self.name]:
        config.extensions_config = config.extensions_config

