import sys
from concurrent.futures import ThreadPoolExecutor
import asyncio

assistant_mode = True
bot = None

def init(model_paths, init_config={}):
  global bot
  sys.path.append(model_paths['path_to_mlc_chatbot_code'])
  from mlc_chatbot.bot import ChatBot
  bot = ChatBot(model_paths['path_to_mlc_pb_home_dir'], model_paths['path_to_mlc_pb_binary_dir'])

async def generate(raw_prompt, length=0, model_params={}, assist=True):
  with ThreadPoolExecutor():
    output = await asyncio.to_thread(bot.send, 
      raw_prompt
    )
  bot.reset()
  return output