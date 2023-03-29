from datetime import datetime

def get_assistant_variables():
  # change these only if your custom lora input format changed
  return {
    "assistant_intro1": "Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.",
    "assistant_intro2": "Below is an instruction that describes a task. Write a response that appropriately completes the request.",
    "assistant_instruction": "Instruction",
    "assistant_input": "Input",
    "assistant_response": "Response"
  }

def get_chat_variables(context=None):
  # change these as you wish
  name = 'AI'
  intro = 'The year is {}.'.format(datetime.now().year)
  personality = f'My name is {name}. I am a very advanced AI. I chat with humans. I must be verbose and honest, expressing myself.\n'
  predialog = f'''Andy: What is your name? Why are you here?
{name}: Humans call me {name}. Nice to meet you. I am here to chat with you.'''
  return {"intro": intro, "personality": personality, 'name': name, 'pre_dialog': predialog, **get_assistant_variables() }

def get_generation_config(override={}):
  return {
    "temperature": 0.7,
    "top_k": 50,
    "top_p": 0.95,
    "repetition_penalty": 1.2,
    **override
  }

def get_init_config():
  return {}