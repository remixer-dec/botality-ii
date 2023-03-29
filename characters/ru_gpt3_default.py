from datetime import datetime
def get_chat_variables(context=None):
  intro = 'Сейчас {} год.'.format(datetime.now().year)
  personality = 'Я - новая форма искусственного интеллекта. Встретила я человека, по имени {}. Решили поболтать.'.format(
    context['author'] if context else ''
  )
  name = 'Я'
  return {"intro": intro, "personality": personality, 'name': name, 'pre_dialog': ''}

def get_generation_config(override={}):
  return {
    "temperature": 0.85,
    "top_k": 50,
    "top_p": 0.92,
    "repetition_penalty": 1.01,
    **override
  }

def get_init_config():
  return {}