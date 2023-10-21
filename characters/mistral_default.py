TEMPLATE_MISTRALITE= '''<|prompter|>{prompt}</s><|assistant|>'''

TEMPLATE_ChatML = '''<|im_start|>system
{system_message}<|im_end|>
<|im_start|>user
{prompt}<|im_end|>
<|im_start|>assistant'''

TEMPLATE_ZEPHIR = '''<|system|>{system_message}</s>
<|user|>
{prompt}</s>
<|assistant|>'''

TEMPLATE_INSTRUCT = '<s>[INST] {prompt} [/INST]'

ALTERNATIVE_SYSTEM_PROMPT = 'Always assist with care, respect, and truth. Respond with utmost utility yet securely. Avoid harmful, unethical, prejudiced, or negative content. Ensure replies promote fairness and positivity.'

ACTIVE_TEMPLATE = TEMPLATE_ChatML

def get_init_config():
  return {'context_size': 4096, 'stop_tokens': ['<|']}

def custom_input_formatter(chronicler, details, fresh=True):
  return ACTIVE_TEMPLATE.format(prompt=details['message'], system_message='This is a conversation in a chat room.')

def custom_output_parser(chronicler, output, chat_id, skip=0):
    output = output[skip:].strip()
    end = (output.find('<|') + 1) or (len(output) + 1)
    return output[:end - 1].strip()

def get_chat_variables(context=None):
  from datetime import datetime
  # change these as you wish
  name = 'Mistral'
  intro = 'The year is {}.'.format(datetime.now().year)
  personality = f'My name is {name}. I am a friendly AI bot in a chat room. I should not be annoying and intrusive.'
  return {"intro": intro, "personality": personality, 'name': name, 'pre_dialog': ''}

def get_generation_config(override):
  return {
    "temperature": 0.7,
    "top_k": 50,
    "top_p": 0.95,
    "repetition_penalty": 1.12,
    **(override or {})
  }
  