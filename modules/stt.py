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

    @dp.message(Command(commands=["stt", "recognize", "transcribe"]), flags={"long_operation": "typing"})
    async def command_stt_handler(message: Message, command: CommandObject) -> None:
      with self.queue.for_user(message.from_user.id) as available:
        if not available:
          return
        if command.command == "stt" and ('-h' in str(command.args) or not (message.reply_to_message and message.reply_to_message.voice)):
          return await message.answer(self.help(dp, bot))
        else:
          error, text = await self.recognize_voice_message(message)
          if error:
            return await message.answer(f"Error, <b>{error}</b>")
          else:
            return await message.answer(f"<i>{text}</i>")

  async def recognize_voice_message(self, message):
    with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as temp_file:
      if not message.voice and (not (message.reply_to_message or message.reply_to_message.voice)):
        return 'Source audio not found', None
      voice = message.reply_to_message.voice if not message.voice else message.voice
      await download_audio(self.bot, voice.file_id, temp_file.name)
      error, data = await self.recognize(temp_file.name)
      return error, data

  async def recognize(self, audio_path):
    wrapped_runner = semaphore_wrapper(self.semaphore, self.model.recognize)
    return await wrapped_runner(audio_path)

  def help(self, dp, bot):
    return f"<b>[Speech-to-text]</b> Usage: /stt@{bot._me.username} *voice_message*"


















