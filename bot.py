import logging
import threading
import time

from aiogram import Bot, Dispatcher
from config_reader import config
from middleware import ChatActionMiddleware, AccessMiddleware, CooldownMiddleware, MediaGroupMiddleware, CounterMiddleware
from misc.botless_layer import CommandRegistrationHijacker

from modules.sd import StableDiffusionModule
from modules.tts import TextToSpeechModule
from modules.admin import AdminModule
from modules.llm import LargeLanguageModel
from modules.tta import TextToAudioModule
from modules.stt import SpeechToTextModule
from modules.extensions import ExtensionsModule

logger = logging.getLogger(__name__)

dp = Dispatcher()
dp.message.middleware(CounterMiddleware(dp))
dp.message.middleware(AccessMiddleware())
dp.message.middleware(ChatActionMiddleware())
dp.message.middleware(CooldownMiddleware())
dp.message.middleware(MediaGroupMiddleware())

CommandRegistrationHijacker(dp)

available_modules = {
  "sd": StableDiffusionModule,
  "tts": TextToSpeechModule,
  "tta": TextToAudioModule,
  "stt": SpeechToTextModule,
  "admin": AdminModule,
  "llm": LargeLanguageModel,
  "extensions": ExtensionsModule
}

def load_module(dp, bot, module):
  dp.modules[module] = available_modules[module](dp, bot)
  dp.timings[module] = round(time.time() - (dp.timings.get('last') or dp.timings['start']), 3)
  if not config.threaded_initialization:
    dp.timings['last'] = time.time()
  logger.info('loaded module: ' + module)

def initialize(dp, bot, threaded=True):
  dp.modules = {}
  dp.counters = {'msg': 0}
  dp.timings = {'start': time.time()}
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
    thread.join(config.sys_request_timeout)
  # initialize extensions after all the other modules
  dp.timings['last'] = time.time()
  load_module(dp, bot, 'extensions')

def main(api=False):
  bot = Bot(token=config.bot_token.get_secret_value(), parse_mode="HTML")
  logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s',)
  initialize(dp, bot, config.threaded_initialization)
  if api:
    from servers.api_sever import init_api_server
    with init_api_server(dp, bot).run_in_thread():
      dp.run_polling(bot)
  else:
    dp.run_polling(bot)


if __name__ == "__main__":
  main()