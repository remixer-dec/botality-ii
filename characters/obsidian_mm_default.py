TEMPLATE = '''<|im_start|>user
{prompt}\n{image}
###
<|im_start|>assistant
'''


def get_init_config():
  return {'context_size': 2048, 'stop_tokens': ['###','<|']}

def custom_input_formatter(chronicler, details, fresh=True):
  has_image = details.get('img_input',{}).get('visual_input', None)
  return TEMPLATE.format(prompt=details['message'], 
    image='<image>' if has_image else '*picture is missing*')

def custom_output_parser(chronicler, output, chat_id, skip=0):
    output = output[skip + 2:].strip()
    end = (output.find('###') + 1) or (output.find('<|') + 1) or (len(output) + 1)
    return output[:end - 1].strip()

def get_chat_variables(context=None):
  from datetime import datetime
  # change these as you wish
  name = 'Obsidian'
  intro = 'The year is {}.'.format(datetime.now().year)
  personality = f'My name is {name}. I am a friendly AI bot in a chat room.'
  return {"intro": intro, "personality": personality, 'name': name, 'pre_dialog': ''}

def get_generation_config(override):
  return {
    "temperature": 0.7,
    "top_k": 50,
    "top_p": 0.95,
    "repetition_penalty": 1.12,
    **(override or {})
  }
  