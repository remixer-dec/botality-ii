def get_init_config():
  return {'context_size': 4096}

def custom_input_formatter(chronicler, details, fresh=True):
  template = f'''Below is an instruction that describes a task. Write a response that appropriately completes the request.

### Instruction: {details['message']}

### Response: '''
  return template

def get_chat_variables(context=None):
  # change these as you wish
  name = 'Assistant'
  intro = 'System:'
  personality = f'You are a helpful, respectful and honest assistant.\nUser:\n'
  return {"intro": intro, "personality": personality, 'name': name, 'pre_dialog': '' }

def custom_output_parser(chronicler, output, chat_id, skip=0):
    output = output[skip:].strip()
    end = (output.find('### ') + 1) or (len(output) + 1)
    return output[:end - 1].strip()

def get_generation_config(override={}):
  return {
    "temperature": 0.6,
    "top_k": 50,
    "top_p": 0.95,
    "repetition_penalty": 1.12,
    **override
  }


