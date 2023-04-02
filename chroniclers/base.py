import abc
import importlib
from collections import defaultdict

class AbstractChronicler(metaclass=abc.ABCMeta):
  def __init__(self, filename):
    chronicler_script = importlib.import_module(filename)
    self.chronicler_script = chronicler_script
    self.vars = chronicler_script.get_chat_variables
    self.gen_cfg = chronicler_script.get_generation_config
    self.init_cfg = chronicler_script.get_init_config

  @abc.abstractmethod
  def prepare(self, details):
    pass

  @abc.abstractmethod
  def parse(self):
    pass

  def prepare_hook(func):
    def wrapper(self, *args, **kwargs):
      if hasattr(self.chronicler_script, 'custom_input_formatter'):
        result = self.chronicler_script.custom_input_formatter(self, *args, **kwargs)
      else:
        result = func(self, *args, **kwargs)
      return result
    return wrapper

  def parse_hook(func):
    def wrapper(self, *args, **kwargs):
      print(args[0])
      if hasattr(self.chronicler_script, 'custom_output_parser'):
        result = self.chronicler_script.custom_output_parser(self, *args, **kwargs)
      else:
        result = func(self, *args, **kwargs)
      return result
    return wrapper


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
    char_vars = self.vars(details)
    if char_vars['pre_dialog']:
      char_vars['pre_dialog'] += '\n'
    dialog = '''{intro}
{personality}

{pre_dialog}{conversation}{name}:'''\
    .format(conversation=conversation, **fresh_vars)
    return dialog

  def parse(self, output, chat_id, skip=0):
    output = output.strip()[skip:]
    print(output)
    end = ((output.find('</s>') + 1) or output.find('\n') + 1 ) or (len(output) + 1)
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

  @AbstractChronicler.prepare_hook
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
  @AbstractChronicler.parse_hook
  def parse(self, output, chat_id, skip=0):
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

  @AbstractChronicler.prepare_hook
  def prepare(self, details, fresh=False):
    msg = details['message']
    return f"""Human: {msg}

Assistant: 
"""
  @AbstractChronicler.parse_hook
  def parse(self, output, chat_id, skip=0):
    output = output[skip:].strip()
    end = (output.find('Human:') + 1 ) or (output.find('Assistant:') + 1) or (len(output) + 1)
    parsed = output[:end - 1].strip()
    if parsed == '':
      return '...'
    return parsed

class GPT4AllChronicler(AbstractChronicler):
  def __init__(self, chronicler_filename):
    super().__init__(chronicler_filename)

  @AbstractChronicler.prepare_hook
  def prepare(self, details, fresh=False):
    msg = details['message'].replace('\n', ' ')
    return f"""{msg}
"""
  @AbstractChronicler.parse_hook
  def parse(self, output, chat_id, skip=0):
    output = output[skip:].strip()
    return output

chroniclers = {
  "alpaca": AlpacaAssistantChronicler,
  "minchatgpt": MinChatGPTChronicler,
  "gpt4all": GPT4AllChronicler,
  "chat": ConversationChronicler
}