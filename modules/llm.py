from aiogram.filters import Command, CommandObject
from aiogram.types import Message, BufferedInputFile, InputMediaPhoto, URLInputFile
from custom_queue import UserLimitedQueue, semaphore_wrapper
from config_reader import config
from aiogram import html, F
from providers.llm_provider import active_model
from chroniclers.base import ConversationChronicler
import asyncio

class LargeLanguageModel:
  def __init__(self, dp, bot, broker):
    self.queue = UserLimitedQueue(config.llm_queue_size_per_user)
    self.semaphore = asyncio.Semaphore(1)
    active_model.init(config.llm_path)
    chatter = ConversationChronicler(config.llm_chronicler, False, config.llm_max_history_items)
    
    @dp.message((F.text[0] if F.text else '') != '/', flags={"long_operation": "typing"})
    async def handle_messages(message: Message):
      with self.queue.for_user(message.from_user.id) as available:
        if available:
          chat_id = message.from_user.id if config.llm_history_grouping == 'user' else message.chat.id
          text = chatter.prepare({
            "message": message.text, 
            "author": message.from_user.full_name.replace(' ', '') or 'User',
            "chat_id": chat_id
          })
          task = await broker.task(semaphore_wrapper(self.semaphore, active_model.generate))\
                             .kiq(text, 64, chatter.cfg(config.llm_generation_cfg_override))
          result = await task.wait_result(timeout=900)
          parsed_output = chatter.parse(result.return_value, chat_id, len(text))
          await message.reply(text=html.quote(parsed_output))

    @dp.message(Command(commands=['reset']))
    async def clear_llm_history(message: Message, command: Command):
      chat_id = message.from_user.id if config.llm_history_grouping == 'user' else message.chat.id
      chatter.history[chat_id] = []

