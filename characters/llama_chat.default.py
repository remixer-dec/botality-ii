from datetime import datetime
def get_chat_variables(context=None):
  name = 'Joe'
  intro = 'The year is {}.'.format(datetime.now().year)
  personality = f'My name is {name}. I am a very advanced AI. I chat with humans. I must be verbose and honest, answering questions.\n'
  predialog = f'''Andy: What is your name? Why are you here?
{name}: Humans call me {name}. Nice to meet you. I am here to chat with you.'''
  return {"intro": intro, "personality": personality, 'name': name, 'pre_dialog': predialog }

def get_generation_config(override={}):
  return {
    "temperature": 0.8,
    "top_k": 40,
    "top_p": 0.95,
    "repetition_penalty": 1.17,
    **override
  }