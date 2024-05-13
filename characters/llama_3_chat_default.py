def get_assistant_variables():
  return {
    "assistant_instruction": "You are a helpful, smart, kind, and efficient AI assistant. You always fulfill the user's requests to the best of your ability."
  }

def get_chat_variables(context=None):
  name = 'Llama'
  personality = 'You are a helpful, smart, kind, and efficient AI assistant. You always fulfill the user\'s requests to the best of your ability.'
  return {"intro": '', "personality": personality, 'name': name, 'pre_dialog': ''}

def get_generation_config(override={}):
  return {
    "temperature": 0.6,
    "top_k": 50,
    "top_p": 0.95,
    "repetition_penalty": 1.12,
    **override
  }

# if true, does not use model-specific chat format
OLD_CHAT_MODE = False 

### FEEL FREE TO EDIT AND CHANGE ALL STUFF ABOVE ^




def get_init_config():
  return { 
    'context_size': 8192,
    'stop_tokens': ['<|eot_id|>', '<|end_of_text|>', '<|start_header_id|>']
  }

def custom_input_formatter(chronicler, details, fresh=True):
  assistant_variables = get_assistant_variables()
  template = f'''<|start_header_id|>system<|end_header_id|>


{assistant_variables['assistant_instruction']}<|eot_id|><|start_header_id|>user<|end_header_id|>


{details['message']}<|eot_id|><|start_header_id|>assistant<|end_header_id|>


'''
  return template

def custom_chat_input_formatter(chronicler, details, fresh=True):
  if fresh:
    chronicler.history[details['chat_id']] = []
  history = chronicler.history[details['chat_id']]
  history.append({"message": details['message'], "author": details['author']})
  while len(history) >= chronicler.max_length:
    history.pop(0)

  char_vars = get_chat_variables(details)
  conversation = f'''<|start_header_id|>system<|end_header_id|>

{char_vars["intro"]}{char_vars["personality"]}<|eot_id|>'''
  
  for item in history:
    msg = item["message"]
    author = chronicler.get_author(char_vars, item)
    conversation += f'''<|start_header_id|>{'user' if author != char_vars['name'] else 'assistant'}<|end_header_id|>

{msg}<|eot_id|>'''
  conversation += '<|start_header_id|>assistant\n\n'
  return conversation

def custom_chat_output_parser(chronicler, output, chat_id, skip=0):
  output = output[skip:].strip()
  chronicler.history[chat_id].append({"message": output, "author": get_chat_variables()["name"]})
  return output

def custom_output_parser(chronicler, output, chat_id, skip=0):
  output = output[skip:].strip()
  end = (output.find('<|eot_id|>:') + 1) or (output.find('<|start_header_id|>') + 1) or (len(output) + 1)
  return output[:end - 1].strip()

if OLD_CHAT_MODE:
  del custom_chat_input_formatter
  del custom_chat_output_parser