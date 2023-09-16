from dotenv import dotenv_values
from utils import cprint
import os
import sys
import json
assert os.path.exists('.env') and os.path.exists('.env.example')

system_env = dotenv_values('.env')
demo_env = dotenv_values('.env.example')

def check_new_keys_in_example_env():
  towrite = '''
'''
  for key in demo_env:
    if key not in system_env:
      towrite += f"{key}='{demo_env[key]}'\n"

  if len(towrite) != 1:
    with open('.env', 'a') as file:
      file.write(towrite)

DEPRECATED_KEYS = [
  'llm_active_model_type', 
  'sd_available_loras', 
  'tts_so_vits_svc_code_path',
  'tts_enable_so_vits_svc',
  'tts_so_vits_svc_base_tts_provider'
]
DEPRECATED_KVS = {
  'llm_assistant_chronicler': ['gpt4all', 'minchatgpt', 'alpaca'],
  'llm_python_model_type': 'cerebras_gpt'
}

def check_deprecated_keys_in_dotenv():
  for key in system_env:
    if key in DEPRECATED_KEYS:
      cprint(f'Warning! The key "{key}" has been deprecated! See CHANGELOG.md.', color='red')
    value = system_env[key]
    if len(value) < 1:
      continue
    if (value[0] != '[' and value[0] != '{'):
      value = f'"{value}"'
    value = json.loads(value)
    if type(value) is str:
      if key in DEPRECATED_KVS and value in DEPRECATED_KVS[key]:
        cprint(f'Warning! The value "{value}" of "{key}" has been deprecated! See CHANGELOG.md.', color='yellow')

check_new_keys_in_example_env()
check_deprecated_keys_in_dotenv()