def get_assistant_variables():
  return {}

def get_chat_variables(context=None):
  return {"intro": '', "personality": '', 'name': 'ASSISTANT', 'pre_dialog': '', **get_assistant_variables() }

def get_generation_config(override={}):
  return {
    "temperature": 0.7,
    "top_k": 50,
    "top_p": 0.95,
    "repetition_penalty": 1.1,
    **override
  }

def custom_input_formatter(chronicler, details, fresh=True):
    msg = details['message'].replace('\n', ' ')
    return f"""{msg}
"""

def custom_output_parser(chronicler, output, chat_id, skip=0):
    output = output[skip:].strip()
    return output

def get_init_config():
  return {'context_size': 2048}