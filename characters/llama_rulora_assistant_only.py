# for https://huggingface.co/IlyaGusev/llama_7b_ru_turbo_alpaca_lora

from datetime import datetime

def custom_input_formatter(chronicler, details, fresh=True):
  lines = details["message"].split('\n')
  query = lines[0]
  is_question = query.endswith('?')
  if len(lines) > 1 or not is_question:
    return f'''Задание: {query}.
Вход: {' '.join(lines[1:]) if len(lines) > 1 else ''}
Выход:'''
  else:
    return f'''Вопрос: {query} 
Выход:'''

def get_assistant_variables():
  return {}

def get_chat_variables(context=None):
  return {"intro": '', "personality": '', 'name': '', 'pre_dialog': '', **get_assistant_variables() }

def get_generation_config(override={}):
  return {
    "temperature": 0.7,
    "top_k": 100,
    "top_p": 0.75,
    "repetition_penalty": 1.16,
    **override
  }

def get_init_config():
  return {}