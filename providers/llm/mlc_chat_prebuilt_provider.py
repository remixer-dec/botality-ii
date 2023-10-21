import sys
from concurrent.futures import ThreadPoolExecutor
from providers.llm.abstract_llm import AbstractLLM
import asyncio
import logging

logger = logging.getLogger(__name__)

class MLCChatPrebuilt(AbstractLLM):
  assistant_mode = True
  def __init__(self, model_paths, init_config):
    sys.path.append(model_paths['path_to_mlc_chatbot_code'])
    try:
      from mlc_chatbot.bot import ChatBot    
    except ImportError:
      logging.error('MLC Chatbot is not installed')
    self.model = ChatBot(model_paths['path_to_mlc_pb_home_dir'], model_paths['path_to_mlc_pb_binary_dir'])
    self.model.generate = self.model.send
    self.filename = 'Unknown model'

  async def generate(self, raw_prompt, length=0, model_params={}, assist=True):
    error = None
    try:
      with ThreadPoolExecutor():
        print(self.model)
        output = await asyncio.to_thread(self.model.generate, 
          raw_prompt
        )
      self.model.reset()
    except Exception as e:
      error = str(e)
    return (False, output) if not error else (error, None)

init = MLCChatPrebuilt