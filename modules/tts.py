from aiogram.filters import Command, CommandObject
from aiogram.types import Message, BufferedInputFile
from providers.tts_provider import init as init_tts, tts, sts, convert_to_ogg, tts_voicemap, sts_voicemap, system_voicemap, tts_authors
from custom_queue import UserLimitedQueue, semaphore_wrapper
from config_reader import config
from utils import download_audio
import asyncio
import tempfile

class TextToSpeechModule:
  def __init__(self, dp, bot):
    self.queue = UserLimitedQueue(config.tts_queue_size_per_user)
    self.semaphore = asyncio.Semaphore(1)
    init_tts(allowRemote=config.tts_mode != 'local', threaded=config.threaded_initialization)
    self.sts_voices = list(sts_voicemap.keys())
    self.all_voices = list(tts_voicemap.keys())
    self.voicemap = tts_voicemap
    self.non_system_voices = [v for v in self.all_voices if v not in system_voicemap]
    self.voices = self.all_voices if config.tts_list_system_voices else self.non_system_voices

    @dp.message(Command(commands=["tts", *self.all_voices]), flags={"long_operation": "record_audio"})
    async def command_tts_handler(message: Message, command: CommandObject) -> None:
      with self.queue.for_user(message.from_user.id) as available:
        if available:
          # show helper message if no voice is selected
          if self.should_print_help(command, message):
            return await message.answer(self.help(dp, bot))

          voice = command.command
          text = str(command.args)
          error, audio = await self.speak(voice, text)
          if error:
            return await message.answer(f"Error, <b>{error}</b>")
          else:
            return await message.answer_voice(voice=audio)
    
    if 'so_vits_svc' in config.tts_enable_backends:
      @dp.message(Command(commands=["revoice", "sts"]), flags={"long_operation": "record_audio"})
      async def revoice(message: Message, command: CommandObject) -> None:
        voice = (str(command.args).split(' ')[0]) if command.args else None
        voice = voice if voice in self.sts_voices else None
        if not voice:
          return await message.answer("<b>Voice not found</b>, available speech-to-speech voices: " +
           ", ".join(self.sts_voices))
        if message.reply_to_message:
          if message.reply_to_message.voice:
            with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as temp_file:
              await download_audio(bot, message.reply_to_message.voice.file_id, temp_file.name)
              wrapped_runner = semaphore_wrapper(self.semaphore, sts)
              error, data = await wrapped_runner(voice, temp_file.name)
              if error:
                return await message.answer(f"Error, <b>{error}</b>")
              else:
                audio = BufferedInputFile(convert_to_ogg(data), 'tts.ogg')
                return await message.answer_voice(voice=audio)
        return await message.answer("No audio found. Use this command replying to voice messages")

    bot.reply_tts = command_tts_handler

  async def speak(self, voice, text):
    wrapped_runner = semaphore_wrapper(self.semaphore, tts)
    error, data = await wrapped_runner(voice, text)
    if data:
      #TODO: async conversion
      audio = BufferedInputFile(convert_to_ogg(data), 'tts.ogg')
      return None, audio
    return error, None
  
  def get_specific_voices(self, language='**', tone='*', allow_system=False):
    return [
        voice
        for voice, voice_info in self.voicemap.items()
        if (
            (allow_system or voice in self.non_system_voices)
            and (language == '**' or voice_info.voice_metamap[voice].get('lang', '**') in ('**', language))
            and (tone == '*' or voice_info.voice_metamap[voice].get('tone', '*') in ('*', tone))
        )
    ]
  
  def should_print_help(self, command, message):
    if command.command == "tts" \
    or not command.args \
    or str(command.args).strip() == "" \
    or ('-help' in str(command.args)):
      return True
    return False
    
  def help(self, dp, bot):
    voice_commands = ' '.join(['/' + x for x in self.voices])
    return f'''<b>[Text-To-Speech]</b> Usage: {voice_commands} text,
Use the commands like /command@{bot._me.username}
[Speech-to-speech] /revoice %voice% *voice_message*
{config.tts_credits} {', '.join(list(tts_authors))}
'''