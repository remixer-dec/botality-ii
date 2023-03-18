import abc
import importlib
from collections import defaultdict

class AbstractChronicler(metaclass=abc.ABCMeta):
  def __init__(self, filename):
    model_adapter = importlib.import_module(filename)
    self.vars = model_adapter.get_chat_variables
    self.cfg = model_adapter.get_generation_config

  @abc.abstractmethod
  def prepare(self, details):
    pass

  @abc.abstractmethod
  def parse(self):
    pass

class ConversationChronicler(AbstractChronicler):
  def __init__(self, chronicler_filename, continous=False, max_length=10):
    super().__init__(chronicler_filename)
    self.history = defaultdict(lambda: [])
    self.max_length = max_length

  def prepare(self, details, fresh=False):
    if fresh:
      self.history = []
    history = self.history[details['chat_id']]
    history.append({"message": details['message'], "author": details['author']})
    if len(history) > self.max_length:
      history.pop(0)
    conversation = ''
    for item in history:
      conversation += f'{item["author"]}: {item["message"]}\n'
    fresh_vars = self.vars(details)
    dialog = '''{intro}
{personality}

{conversation}{name}:'''.format(conversation=conversation, **fresh_vars)
    return dialog

  def parse(self, output, chat_id, skip=0):
    output = output[skip:]
    parsed = output[0: output.find('\n')]
    self.history[chat_id].append({"message": parsed, "author": self.vars()['name']})
    return parsed


