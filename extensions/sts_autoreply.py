import random
from config_reader import config
from types import SimpleNamespace
from aiogram import F
from aiogram.types import Message
from extensions._base_extension import BaseExtension, BaseExtensionConfig
from utils import raise_rail_exceptions
from typing_extensions import Literal, Union

class ExtensionConfig(BaseExtensionConfig):
  mode: Literal['assist', 'chat'] = 'chat'
  reply_with_tts: bool = True
  reply_tts_voice: Union[str, Literal['random', 'random_per_user']] = 'random_per_user'

class STTAutoreplyExtension(BaseExtension):
  '''Automatically replies to voice messages'''

  name = 'stt_autoreply'
  dependencies = ('stt', 'llm', 'tts')

  def __init__(self, dp, bot):
    super().__init__(ExtensionConfig)
    stt, llm, tts = (dp.modules['stt'], dp.modules['llm'], dp.modules['tts'])
    voice_pool = tts.get_specific_voices(config.lang, '*')
    self.cache = {}

    def _get_voice(cfg_voice):
      voice = cfg_voice or voice_pool[0]
      voice = random.choice(tts.sts_voices) if 'random' in voice else voice

    @dp.message((F.voice), flags={"long_operation": "record_audio", "name": 'voice_message_filter'})
    async def handle_voice_messages(message: Message):
      try:
        # do not self-trigger
        print(message)
        if message.from_user.id == bot._me.id:
          return
        assert len(voice_pool) > 0, f'no {config.lang} voices found'
        # recognize voice message
        text = raise_rail_exceptions(*await stt.recognize_voice_message(message))
        # set llm handler
        llm_call_func = llm.assist if self.config.mode == 'assist' else llm.chat
        # send recognized text to the llm
        reply = await llm_call_func(text, llm.get_common_chat_attributes(message))
        if self.config.reply_with_tts:
          # get voice name for replying
          voice = _get_voice(self.config.reply_tts_voice)
          # handle caching of random voices
          if self.config.reply_tts_voice == 'random_per_user':
            voice = self.cache.setdefault(message.from_user.id, voice)
          await bot.reply_tts(message=message, command=SimpleNamespace(command=voice, args=[reply]))
        else:
          return await message.answer(reply)
      except Exception as e:
        return await message.answer(f"Error, <b>{e}</b>")

extension = STTAutoreplyExtension