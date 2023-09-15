from abc import ABCMeta, abstractmethod

class AbstractTTS(metaclass=ABCMeta):
  def __init__(self):
    pass

  @abstractmethod
  def speak(self, voice, text):
    pass

class AbstractSTS(metaclass=ABCMeta):
  def __init__(self, tts_instance):
    self.tts = tts_instance
    pass

  @abstractmethod
  def mimic(self, voice, original_audio):
    pass

  @abstractmethod
  def speak():
    pass
