from aiogram.filters import Command, CommandObject
from aiogram.types import Message, BufferedInputFile, InputMediaPhoto, URLInputFile
from custom_queue import UserLimitedQueue, semaphore_wrapper
from config_reader import config
from aiogram import html, F
from providers.llm_provider import active_model
from chroniclers.base import chroniclers
from types import SimpleNamespace
from utils import parse_photo, tg_image_to_data
import asyncio
import json

def get_chat_id(message):
  return message.from_user.id if config.llm_history_grouping == 'user' else message.chat.id

def assistant_model_available(model):
  return (hasattr(model, 'assistant_mode') and model.assistant_mode) or \
    config.llm_force_assistant_for_unsupported_models

def visual_mode_available(model):
  return (hasattr(model, 'visual_mode') and model.assistant_mode)

class LargeLanguageModel:
  def __init__(self, dp, bot):
    self.queue = UserLimitedQueue(config.llm_queue_size_per_user)
    self.semaphore = asyncio.Semaphore(1)
    chatter = chroniclers['chat'](config.llm_character, False, config.llm_max_history_items)
    assistant = chroniclers[config.llm_assistant_chronicler](config.llm_character)
    initialized_model = active_model.init(config.llm_paths, chatter.init_cfg())
    cfg_override = config.llm_generation_cfg_override
    
    @dp.message((F.text[0] if F.text else '') != '/', flags={"long_operation": "typing"})
    async def handle_messages(message: Message):
      with self.queue.for_user(message.from_user.id) as available:
        if available:
          if (config.llm_assistant_use_in_chat_mode and assistant_model_available(active_model))\
            or (visual_mode_available(active_model) and parse_photo(message)):
            return await assist(message=message, command=SimpleNamespace(args=message.text))
          text = chatter.prepare({
            "message": message.text, 
            "author": message.from_user.first_name.replace(' ', '') or 'User',
            "chat_id": get_chat_id(message)
          })
          wrapped_runner = semaphore_wrapper(self.semaphore, active_model.generate)
          result = await wrapped_runner(text, config.llm_max_tokens, chatter.gen_cfg(cfg_override))
          parsed_output = chatter.parse(result, get_chat_id(message), len(text))
          await message.reply(text=html.quote(parsed_output))

    @dp.message(Command(commands=['reset', 'clear']), flags={"cooldown": 20})
    async def clear_llm_history(message: Message, command: Command):
      chatter.history[get_chat_id(message)] = []
    
    @dp.message(Command(commands=['ask', 'assist']), flags={"long_operation": "typing"})
    async def assist(message: Message, command: Command):
      msg = str(command.args).strip()
      if msg and command.args:
        with self.queue.for_user(message.from_user.id) as available:
          if available:
            if not assistant_model_available(active_model):
              return await message.reply(text='Assistant model is not available')
            img_input = {"visual_input": await tg_image_to_data(parse_photo(message), bot)}\
                        if visual_mode_available(active_model) \
                        else {}
            text = assistant.prepare({
              "message": msg, 
              "author": message.from_user.first_name.replace(' ', '') or 'User',
              "chat_id": get_chat_id(message),
              "model": initialized_model
            })
            wrapped_runner = semaphore_wrapper(self.semaphore, active_model.generate)
            result = await wrapped_runner(text, config.llm_max_tokens, chatter.gen_cfg(cfg_override), **img_input)
            parsed_output = assistant.parse(result.return_value, get_chat_id(message), len(text))
            if config.llm_assistant_use_in_chat_mode and not hasattr(command, 'command'):
              reply = html.quote(parsed_output)
            else:
              reply = f'<b>Q</b>: {msg}\n\n<b>A</b>: {html.quote(parsed_output)}'
            await message.reply(text=(reply), allow_sending_without_reply=True)

    @dp.message(Command(commands=['llm']), flags={"cooldown": 20})
    async def helpfunction(message: Message, command: Command):
      text = f'''[LLM module].
      Commands: /ask
      Active model type: {config.llm_active_model_type}
      Assistant mode: {str(assistant_model_available(active_model))} ({config.llm_assistant_chronicler})
      Character: {config.llm_character}
      Context visibility: {config.llm_history_grouping}
      Model: {initialized_model.get('filename') if initialized_model else 'unknown'}
      Config: 
{json.dumps(chatter.gen_cfg(config.llm_assistant_cfg_override), sort_keys=True, indent=4)}'''
      return await message.reply(text=text)