from aiogram.filters import Command, CommandObject
from aiogram.types import Message, BufferedInputFile, InputMediaPhoto, URLInputFile
from custom_queue import UserLimitedQueue, semaphore_wrapper
from config_reader import config
from aiogram import html, F
from providers.llm_provider import active_model
from chroniclers.base import ConversationChronicler, AssistantChronicler
from types import SimpleNamespace
import asyncio

def get_chat_id(message):
  return message.from_user.id if config.llm_history_grouping == 'user' else message.chat.id

class LargeLanguageModel:
  def __init__(self, dp, bot, broker):
    self.queue = UserLimitedQueue(config.llm_queue_size_per_user)
    self.semaphore = asyncio.Semaphore(1)
    active_model.init(config.llm_paths)
    chatter = ConversationChronicler(config.llm_character, False, config.llm_max_history_items)
    assistant = AssistantChronicler(config.llm_character)
    
    @dp.message((F.text[0] if F.text else '') != '/', flags={"long_operation": "typing"})
    async def handle_messages(message: Message):
      with self.queue.for_user(message.from_user.id) as available:
        if available:
          if config.llm_assistant_use_in_chat_mode \
          and hasattr(active_model, 'submodel')  \
          and active_model.submodel:
            return await assist(message=message, command=SimpleNamespace(args=message.text))
          text = chatter.prepare({
            "message": message.text, 
            "author": message.from_user.first_name.replace(' ', '' or 'User'),
            "chat_id": get_chat_id(message)
          })
          task = await broker.task(semaphore_wrapper(self.semaphore, active_model.generate))\
                             .kiq(text, 64, chatter.cfg(config.llm_generation_cfg_override))
          result = await task.wait_result(timeout=900)
          parsed_output = chatter.parse(result.return_value, get_chat_id(message), len(text))
          await message.reply(text=html.quote(parsed_output))

    @dp.message(Command(commands=['reset', 'clear']))
    async def clear_llm_history(message: Message, command: Command):
      chatter.history[get_chat_id(message)] = []
    
    @dp.message(Command(commands=['ask', 'assist']), flags={"long_operation": "typing"})
    async def assist(message: Message, command: Command):
      msg = str(command.args).strip()
      if msg:
        with self.queue.for_user(message.from_user.id) as available:
          if available:
            text = assistant.prepare({
              "message": msg, 
              "author": message.from_user.first_name.replace(' ', '') or 'User',
              "chat_id": get_chat_id(message)
            })
            task = await broker.task(semaphore_wrapper(self.semaphore, active_model.generate))\
                               .kiq(text, 128, chatter.cfg(config.llm_assistant_cfg_override), True)
            result = await task.wait_result(timeout=900)
            parsed_output = assistant.parse(result.return_value, get_chat_id(message), len(text))
            await message.reply(text=html.quote(parsed_output))
        
