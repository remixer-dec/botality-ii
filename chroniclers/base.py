import abc
import importlib
from collections import defaultdict

class AbstractChronicler(metaclass=abc.ABCMeta):
  def __init__(self, filename):
    model_adapter = importlib.import_module(filename)
    self.vars = model_adapter.get_chat_variables
    self.gen_cfg = model_adapter.get_generation_config
    self.init_cfg = model_adapter.get_init_config

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
      self.history[details['chat_id']] = []
    history = self.history[details['chat_id']]
    history.append({"message": details['message'], "author": details['author']})
    while len(history) >= self.max_length:
      history.pop(0)
    conversation = ''
    for item in history:
      msg = item["message"]
      conversation += f'{item["author"]}: {msg[0].upper() + msg[1:]}\n'
    fresh_vars = self.vars(details)
    if fresh_vars['pre_dialog']:
      fresh_vars['pre_dialog'] += '\n'
    dialog = '''{intro}
{personality}

{pre_dialog}{conversation}{name}:'''\
    .format(conversation=conversation, **fresh_vars)
    return dialog

  def parse(self, output, chat_id, skip=0):
    print(output)
    output = output[skip:].strip()
    end = (output.find('\n') + 1 ) or (output.find('</s>') + 1) or (len(output) + 1)
    parsed = output[:end - 1].strip()
    if parsed == '':
      return '...'
    author = self.vars()['name']
    repeated_string_index = next((i for i, d in enumerate(self.history[chat_id]) if (d['message'] == parsed and d["author"] == author)), None)
    if repeated_string_index:
      self.history[chat_id].append({"message": '???', "author": author})
    else:
      self.history[chat_id].append({"message": parsed.replace(':', ''), "author": author})
    return parsed


class AlpacaAssistantChronicler(AbstractChronicler):
  def __init__(self, chronicler_filename):
    super().__init__(chronicler_filename)

  def prepare(self, details, fresh=False):
    msg = details['message'].split('\n', 1)
    l = self.vars(details)
    if len(msg) > 1:
      return f"""{l['assistant_intro1']} 
### {l['assistant_instruction']}:
{msg[0]}
### {l['assistant_input']}:
{msg[1]}
### {l['assistant_response']}:
"""
    else:
      return f"""{l['assistant_intro2']} 
### {l['assistant_instruction']}:
{msg[0]}
### {l['assistant_response']}:
"""
  def parse(self, output, chat_id, skip=0):
    print(output)
    output = output[skip:]
    end = output.find('</s>')
    if end == -1:
      end = output.find('###')
    parsed = output[0: end if end != -1 else None].strip()
    if parsed == '':
      return '...'
    return parsed

class MinChatGPTChronicler(AbstractChronicler):
  def __init__(self, chronicler_filename):
    super().__init__(chronicler_filename)

  def prepare(self, details, fresh=False):
    msg = details['message']
    return f"""Human: {msg}

Assistant: 
"""
  def parse(self, output, chat_id, skip=0):
    print(output)
    output = output[skip:].strip()
    end = (output.find('Human:') + 1 ) or (output.find('Assistant:') + 1) or (len(output) + 1)
    parsed = output[:end - 1].strip()
    if parsed == '':
      return '...'
    return parsed

chroniclers = {
  "alpaca": AlpacaAssistantChronicler,
  "minchatgpt": MinChatGPTChronicler,
  "chat": ConversationChronicler
}