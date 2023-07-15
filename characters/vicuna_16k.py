from datetime import datetime

VERSION = 1.1

def get_assistant_variables():
  # change these only if your custom lora input format changed
  if VERSION == 1.1:
    intro = "A chat between a curious user and an artificial intelligence assistant. The assistant gives helpful, detailed, and polite answers to the user's questions."
    assistant_instruction = "USER"
    assistant_response = "ASSISTANT"
  return {
    "assistant_intro1": intro,
    "assistant_intro2": intro,
    "assistant_instruction": assistant_instruction,
    "assistant_input": False,
    "assistant_response": assistant_response
  }

def get_chat_variables(context=None):
  # change these as you wish
  assistant_variables = get_assistant_variables()
  name = 'AI'
  intro = 'The year is {}.'.format(datetime.now().year)
  personality = f'My name is {name}. I am a very advanced AI. I chat with humans. I must be verbose and honest, expressing myself.\n'
  return {"intro": intro, "personality": personality, 'name': name, 'pre_dialog': '', **get_assistant_variables() }

def get_generation_config(override={}):
  return {
    "temperature": 0.82,
    "top_k": 72,
    "top_p": 0.21,
    "repetition_penalty": 1.19,
    **override
  }

def get_init_config(): 
  # rope_freq_scale = 1 / (max_seq_len / 2048)
  return {'context_size': 16092, 'rope_freq_base': 10000, 'rope_freq_scale': 0.125}