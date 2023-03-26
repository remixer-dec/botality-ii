from datetime import datetime
def get_chat_variables(context=None):
  intro = 'Сейчас {} год.'.format(datetime.now().year)
  personality = 'Я - новая форма искусственного интеллекта. Встретила я человека, по имени {}. Решили поболтать.\n'.format(
    context['author'] if context else ''
  )
  name = 'Я'
  return {"intro": intro, "personality": personality, 'name': name}

def get_generation_config(override={}):
  return {
    "temperature": 1.0,
    "top_k": 50,
    "top_p": 0.92,
    "repetition_penalty": 1.01,
    **override
  }