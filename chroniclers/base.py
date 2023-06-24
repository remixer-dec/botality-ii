import importlib
from abc import ABCMeta, abstractmethod
from collections import defaultdict

class AbstractChronicler(metaclass=ABCMeta):
  def __init__(self, filename):
    chronicler_script = importlib.import_module(filename)
    self.chronicler_script = chronicler_script
    self.vars = chronicler_script.get_chat_variables
    self.gen_cfg = chronicler_script.get_generation_config
    self.init_cfg = chronicler_script.get_init_config

  @abstractmethod
  def prepare(self, details):
    pass

  @abstractmethod
  def parse(self):
    pass
  
  @staticmethod
  def prepare_hook(func):
    def wrapper(self, *args, **kwargs):
      formatter = getattr(self.chronicler_script, 'custom_input_formatter', func)
      return formatter(self, *args, **kwargs)
    return wrapper

  @staticmethod
  def parse_hook(func):
    def wrapper(self, *args, **kwargs):
      print(args[0])
      parser = getattr(self.chronicler_script, 'custom_output_parser', func)
      return parser(self, *args, **kwargs)
    return wrapper

class AssistantReplyChronicler(AbstractChronicler):
  def __init__(self, chronicler_filename):
    super().__init__(chronicler_filename)

  def prepare(self, details, fresh=False):
    text = details['message']
    reply_text = details['reply_text']
    memory = self.parse_qa(reply_text) + '\n' + text
    details['message'] = memory
    return chroniclers['instruct'].prepare(self, details)
  
  def parse_qa(self, text):
    if text.startswith('Q:'):
      splits = text.split('\n\n')
      return f'>{splits[0][2:]}\n>{splits[1][2:]}'
    else:
      return '>' + text.replace('\n', ' ')

  def parse(self, output, chat_id, skip=0):
    return chroniclers['instruct'].parse(self, output, chat_id, skip)


class ConversationChronicler(AbstractChronicler):
  def __init__(self, chronicler_filename, continous=False, max_length=10):
    super().__init__(chronicler_filename)
    self.history = defaultdict(lambda: [])
    self.max_length = max_length

  def get_author(self, vars, item):
    r_username = vars.get('replace_username', False)
    return r_username if r_username and item['author'] != vars['name'] else item['author']

  def prepare(self, details, fresh=False):
    if fresh:
      self.history[details['chat_id']] = []
    history = self.history[details['chat_id']]
    history.append({"message": details['message'], "author": details['author']})
    while len(history) >= self.max_length:
      history.pop(0)
    conversation = ''
    char_vars = self.vars(details)
    for item in history:
      msg = item["message"]
      author = self.get_author(char_vars, item)
      conversation += f'{author}: {msg[0].upper() + msg[1:]}\n'
    if char_vars['pre_dialog']:
      char_vars['pre_dialog'] += '\n'
    dialog = '''{intro}
{personality}

{pre_dialog}{conversation}{name}:'''\
    .format(conversation=conversation, **char_vars)
    return dialog

  def parse(self, output, chat_id, skip=0):
    output = output.strip()[skip:]
    print(output)
    end = ((output.find('</s>') + 1) or output.find('\n') + 1 ) or (len(output) + 1)
    parsed = output[:end - 1].strip()
    if parsed == '':
      return '...'
    author = self.vars()['name']
    self.history[chat_id].append({"message": parsed.replace(':', ''), "author": author})
    return parsed


class AlpacaAssistantChronicler(AbstractChronicler):
  def __init__(self, chronicler_filename):
    super().__init__(chronicler_filename)

  @AbstractChronicler.prepare_hook
  def prepare(self, details, fresh=False):
    msg = details['message'].split('\n', 1)
    l = self.vars(details)
    if len(msg) > 1 and l['assistant_input']:
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

class RawChronicler(AbstractChronicler):
  def __init__(self, chronicler_filename):
    super().__init__(chronicler_filename)
  
  def prepare(self, details, fresh=False):
    return details['message']

  def parse(self, output, chat_id, skip=0):
    print(output)
    return output


chroniclers = {
  "alpaca": AlpacaAssistantChronicler,
  "instruct": AlpacaAssistantChronicler,
  "chat": ConversationChronicler,
  "reply": AssistantReplyChronicler,
  "raw": RawChronicler
}