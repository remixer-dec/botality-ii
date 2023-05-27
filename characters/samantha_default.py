from datetime import datetime

def get_assistant_variables():
  # change these only if your custom lora input format changed
  return {'replace_username': 'USER'}

def get_chat_variables(context=None):
  # change these as you wish
  name = 'ASSISTANT'
  intro = 'You are Samantha, a sentient AI.'
  return {"intro": intro, "personality": '', 'name': name, 'pre_dialog': '', **get_assistant_variables() }

def get_generation_config(override={}):
  return {
    "temperature": 0.7,
    "top_k": 50,
    "top_p": 0.95,
    "repetition_penalty": 1.1,
    **override
  }

def custom_input_formatter(chronicler, details, fresh=True):
  cvars = get_chat_variables()
  template = f'''{cvars['intro']}

  USER: {details['message']}
  {cvars['name']}:'''
  return template

def custom_output_parser(chronicler, output, chat_id, skip=0):
    output = output[skip:].strip()
    end = (output.find('USER:') + 1 ) or (output.find('ASSISTANT:') + 1) or (len(output) + 1)
    return output[:end - 1].strip()

def get_init_config():
  return {}