#Reference: https://github.com/IlyaGusev/rulm/blob/master/self_instruct/src/interact_llamacpp.py
#License: Apache License 2.0

from llama_cpp import Llama

SYSTEM_PROMPT = "Ты — Сайга, русскоязычный автоматический ассистент. Ты разговариваешь с людьми и помогаешь им."
SYSTEM_TOKEN = 1788
USER_TOKEN = 1404
BOT_TOKEN = 9225
LINEBREAK_TOKEN = 13

ROLE_TOKENS = {
    "user": USER_TOKEN,
    "bot": BOT_TOKEN,
    "system": SYSTEM_TOKEN
}

def get_message_tokens(model, role, content):
    message_tokens = model.tokenize(content.encode("utf-8"))
    message_tokens.insert(1, ROLE_TOKENS[role])
    message_tokens.insert(2, LINEBREAK_TOKEN)
    message_tokens.append(model.token_eos())
    return message_tokens

def get_system_tokens(model):
    system_message = {
        "role": "system",
        "content": SYSTEM_PROMPT
    }
    return get_message_tokens(model, **system_message)

def get_assistant_variables():
  # change these only if your custom lora input format changed
  return {'replace_username': 'User'}

def get_chat_variables(context=None):
  # change these as you wish
  name = 'Saiga'
  intro = SYSTEM_PROMPT
  return {"intro": intro, "personality": '', 'name': name, 'pre_dialog': '', **get_assistant_variables() }

def get_generation_config(override={}):
  return {
    "temperature": 0.2,
    "top_k": 30,
    "top_p": 0.9,
    "repetition_penalty": 1.1,
    **override
  }

def custom_input_formatter(chronicler, details, fresh=True):
  model = details['model']['instance']
  tokens = get_system_tokens(model)
  message_tokens = get_message_tokens(model=model, role="user", content=details['message'])
  role_tokens = [model.token_bos(), BOT_TOKEN, LINEBREAK_TOKEN]
  tokens += message_tokens + role_tokens
  # detokinization is used for compatibility with moldel(), since model.generate is not supported
  return model.detokenize(tokens).decode("utf-8")

def custom_output_parser(chronicler, output, chat_id, skip=0):
    output = output[skip:].strip()
    end = (output.find('User:') + 1 ) or (output.find('Saiga:') + 1) or (len(output) + 1)
    return output[:end - 1].strip()

def get_init_config():
  return {'context_size': 2000}