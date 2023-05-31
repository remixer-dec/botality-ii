from dotenv import dotenv_values
import os
assert os.path.exists('.env') and os.path.exists('.env.example')

system_env = dotenv_values('.env')
demo_env = dotenv_values('.env.example')

towrite = '''
'''

for key in demo_env:
  if key not in system_env:
    towrite += f"{key}='{demo_env[key]}'\n"

if len(towrite) != 1:
  with open('.env', 'a') as file:
    file.write(towrite)