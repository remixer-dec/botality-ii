ORCA_VERSION = 2

def get_assistant_variables():
  return {}

def get_chat_variables(context=None):
  intro = 'You are an AI assistant that follows instruction extremely well. Help as much as you can.'
  return {"intro": intro, "personality": '', 'name': 'ASSISTANT', 'pre_dialog': ''}

def get_generation_config(override={}):
  return {
    "temperature": 0.7,
    "top_k": 50,
    "top_p": 0.95,
    "repetition_penalty": 1.1,
    **override
  }

def custom_input_formatter(chronicler, details, fresh=True):
  msg = details['message']
  n = '\n'
  if not msg.startswith('>') and '\n' in msg:
    msg = msg.split('\n', 1)
  else:
    msg = [msg]
  template = f'''### System:
You are an AI assistant that follows instruction extremely well. Help as much as you can.

### User:
{msg[0]}

### Response:
''' if ORCA_VERSION == 1 else f'''### System:
You are an AI assistant that follows instruction extremely well. Help as much as you can.

### User:
{msg[0]}

### Input:{(n + msg[1]) if len(msg) > 1 else ""}

### Response:
'''
  return template

def custom_output_parser(chronicler, output, chat_id, skip=0):
    output = output[skip:].strip()
    end = (output.find('###') + 1) or (len(output) + 1)
    return output[:end - 1].strip()

def get_init_config():
  return {'context_size': 2048}