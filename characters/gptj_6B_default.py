from datetime import datetime
def get_chat_variables(context=None):
  intro = 'The year is {}.'.format(datetime.now().year)
  personality = 'I am a very advanced AI from another planet. I met a person, their name is {}.\n'.format(
    context['author'] if context else ''
  )
  name = 'AI'
  return {"intro": intro, "personality": personality, 'name': name, 'pre_dialog': ''}

def get_generation_config(override={}):
  return {
    "temperature": 0.8,
    "top_k": 40,
    "top_p": 1,
    "repetition_penalty": 1.01,
    **override
  }