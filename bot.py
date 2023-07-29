import logging
import automigration

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


def initialize(dp, bot):
  available_modules = {
    "sd": StableDiffusionModule,
    "tts": TextToSpeechModule,
    "tta": TextToAudioModule,
    "stt": SpeechToTextModule,
    "admin": AdminModule,
    "llm": LargeLanguageModel
  }
  dp['modules'] = {}
  for module in config.active_modules:
    if module in available_modules:
      dp['modules'][module] = available_modules[module](dp, bot)

def main():
  bot = Bot(token=config.bot_token.get_secret_value(), parse_mode="HTML")
  logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s',)
  initialize(dp, bot)
  print('running')
  dp.run_polling(bot)


if __name__ == "__main__":
  main()