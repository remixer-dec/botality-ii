from abc import ABCMeta, abstractmethod


class AbstractSTT(metaclass=ABCMeta):
  model = None
  def __init__(self):
    return None

  @abstractmethod
  def recognize(self, audio_path):
    pass