from aiogram.filters import Command, CommandObject
from aiogram.types import Message, BufferedInputFile
from providers.tts_provider import convert_to_ogg
from providers.tta_provider import generate_audio_async, tta_init
from custom_queue import UserLimitedQueue, semaphore_wrapper
from config_reader import config
import asyncio

class TextToAudioModule:
  def __init__(self, dp, bot):
    self.queue = UserLimitedQueue(config.tta_queue_size_per_user)
    self.semaphore = asyncio.Semaphore(1)
    
    if 'tta' in config.active_modules:
      self.available = tta_init()
    if not self.available:
      return

    @dp.message(Command(commands=["tta", "sfx", "music"]), flags={"long_operation": "record_audio"})
    async def command_tta_handler(message: Message, command: CommandObject) -> None:
      with self.queue.for_user(message.from_user.id) as available:
        if not available:
          return
        if command.command == "tta" or not command.args or str(command.args).strip() == "" or ('-help' in str(command.args)):
          return await message.answer(self.help(dp, bot))
        else:
          audio_type = command.command
          text = str(command.args)
          wrapped_runner = semaphore_wrapper(self.semaphore, generate_audio_async)
          error, data = await wrapped_runner(text, audio_type, config.tta_duration)
          print(error, data)
          if error:
            return await message.answer(f"Error, <b>{error}</b>")
          else:
            audio = BufferedInputFile(convert_to_ogg(data), 'audio.ogg')
            return await message.answer_voice(voice=audio)
  def help(self, dp, bot):
    return f'''<b>[Text-To-Audio]</b> Usage:
/sfx@{bot._me.username} prompt
/music{bot._me.username} prompt'''



















