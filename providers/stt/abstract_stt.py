from abc import ABCMeta, abstractmethod


class AbstractSTT(metaclass=ABCMeta):
  model = None
  def __init__(self, model_paths, init_config):
    return self

  @abstractmethod
  def recognize(self, audio_path):
    pass