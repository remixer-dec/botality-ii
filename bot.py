import logging
import threading

from aiogram import Bot, Dispatcher
from config_reader import config
from middleware import ChatActionMiddleware, AccessMiddleware, CooldownMiddleware, MediaGroupMiddleware

from modules.sd import StableDiffusionModule
from modules.tts import TextToSpeechModule
from modules.admin import AdminModule
from modules.llm import LargeLanguageModel
from modules.tta import TextToAudioModule
from modules.stt import SpeechToTextModule

logger = logging.getLogger(__name__)

dp = Dispatcher()
dp.message.middleware(AccessMiddleware())
dp.message.middleware(ChatActionMiddleware())
dp.message.middleware(CooldownMiddleware())
dp.message.middleware(MediaGroupMiddleware())

available_modules = {
  "sd": StableDiffusionModule,
  "tts": TextToSpeechModule,
  "tta": TextToAudioModule,
  "stt": SpeechToTextModule,
  "admin": AdminModule,
  "llm": LargeLanguageModel
}

def load_module(dp, bot, module):
  dp['modules'][module] = available_modules[module](dp, bot)
  logger.info('loaded module: ' + module)

def initialize(dp, bot, threaded=True):
  dp['modules'] = {}
  threads = []
  for module in config.active_modules:
    if module in available_modules:
      if not threaded:
        load_module(dp, bot, module)
        continue
      thread=threading.Thread(target=load_module, args=(dp, bot, module))
      thread.start()
      threads.append(thread)
  for thread in threads:
    thread.join()

def main(api=False):
  bot = Bot(token=config.bot_token.get_secret_value(), parse_mode="HTML")
  logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s',)
  initialize(dp, bot, config.threaded_initialization)
  if api:
    from servers.api_sever import init_api_server
    with init_api_server(dp).run_in_thread():
      dp.run_polling(bot)
  else:
    dp.run_polling(bot)


if __name__ == "__main__":
  main()