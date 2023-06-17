from abc import ABCMeta, abstractmethod
from collections import defaultdict

class AbstractLLM(metaclass=ABCMeta):
  assistant_mode = True
  model = None
  def __init__(self, model_paths, init_config):
    return self

  def tokenize(self, details):
    pass

  @abstractmethod
  def generate(self, prompt, length, model_params, assist):
    pass
  
