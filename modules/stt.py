from aiogram.filters import Command, CommandObject
from aiogram.types import Message, BufferedInputFile
from aiogram import html, F
from providers.stt_provider import active_model
from custom_queue import UserLimitedQueue, semaphore_wrapper
from config_reader import config
from utils import download_audio
from types import SimpleNamespace
import random
import tempfile
import asyncio

class SpeechToTextModule:
  def __init__(self, dp, bot):
    self.queue = UserLimitedQueue(config.stt_queue_size_per_user)
    self.semaphore = asyncio.Semaphore(1)
    self.bot = bot
    self.model = active_model.init()
    self.cache = {}
    
    if config.stt_autoreply_mode: # TODO: move this to separate module after implementing extensions
      @dp.message((F.voice), flags={"long_operation": "record_audio"})
      async def handle_voice_messages(message: Message):
        error, text = await self.recognize_voice_message(message)
        if text and 'llm' in config.active_modules:
          llm = dp['modules']['llm']
          tts = dp['modules']['tts']
          llm_call_func = llm.assist if config.stt_autoreply_mode == 'assist' else llm.chat
          reply = await llm_call_func(text, llm.get_common_chat_attributes(message))
          if 'tts' in config.active_modules:
            voice = config.stt_autoreply_voice or tts.voices[0]
            voice = random.choice(tts.voices) if voice == 'random' else voice
            voice = self.cache.setdefault(message.from_user.id, voice if type(voice) is str else voice['voice'])
            await bot.reply_tts(message=message, command=SimpleNamespace(command=voice, args=[reply]))
          else:
            return await message.answer(reply)
        if error:
          return await message.answer(f"Error, <b>{error}</b>")

    @dp.message(Command(commands=["stt", "recognize", "transcribe"]), flags={"long_operation": "typing"})
    async def command_stt_handler(message: Message, command: CommandObject) -> None:
      with self.queue.for_user(message.from_user.id) as available:
        if not available:
          return
        if command.command == "stt" and ('-h' in str(command.args) or not (message.reply_to_message and message.reply_to_message.voice)):
          return await message.answer(f"Usage: /stt [voice_message] \nUse the commands like /command@botname")
        else:
          error, text = await self.recognize_voice_message(message)
          if error:
            return await message.answer(f"Error, <b>{error}</b>")
          else:
            return await message.answer(f"<i>{text}</i>")

  async def recognize_voice_message(self, message):
    with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as temp_file:
      voice = message.reply_to_message.voice if not message.voice else message.voice
      await download_audio(self.bot, voice.file_id, temp_file.name)
      wrapped_runner = semaphore_wrapper(self.semaphore, self.recognize)
      error, data = await wrapped_runner(temp_file.name)
      return error, data

  async def recognize(self, audio_path):
    return await self.model.recognize(audio_path)



















