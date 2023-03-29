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
    "temperature": 0.9,
    "top_k": 200,
    **override
  }

def get_init_config():
  return {
    "use_tiktoken": True,
    "nanogpt": True
  }