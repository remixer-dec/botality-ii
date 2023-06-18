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
  async def assist(self, text, context):
    prompt = self.assistant.prepare({
      "message": text, 
      "model": self.model,
      **context
    })
    wrapped_runner = semaphore_wrapper(self.semaphore, self.model.generate)
    params = {**self.assistant.gen_cfg(self.assistant_cfg_override), **context.get('img_input',{})}
    error, result = await wrapped_runner(prompt, config.llm_max_assistant_tokens, params)
    output = self.assistant.parse(result, context.get('chat_id', 0), len(prompt)) if not error else str(result)
    return output

  async def chat(self, text, context):
    prompt = self.chatter.prepare({
      "message": text, 
      **context
    })
    wrapped_runner = semaphore_wrapper(self.semaphore, self.model.generate)
    cfg = self.chatter.gen_cfg(self.chat_cfg_override)
    error, result = await wrapped_runner(prompt, config.llm_max_tokens, cfg)
    return self.chatter.parse(result, context['chat_id'], len(prompt)) if not error else str(result)

  def raw_llm(self, text, content):
    pass

  def get_common_chat_attributes(self, message, additional={}):
    return {
      'author': message.from_user.first_name.replace(' ', '') or 'User',
      'chat_id': get_chat_id(message),
      'user_id': message.from_user.id,
      **additional
    }

  def __init__(self, dp, bot):
    self.queue = UserLimitedQueue(config.llm_queue_size_per_user)
    self.semaphore = asyncio.Semaphore(1)
    self.chatter = chroniclers['chat'](config.llm_character, False, config.llm_max_history_items)
    self.assistant = chroniclers[config.llm_assistant_chronicler](config.llm_character)
    model = active_model.init(config.llm_paths, self.chatter.init_cfg())
    self.model = model
    self.chat_cfg_override = config.llm_generation_cfg_override
    self.assistant_cfg_override = config.llm_assistant_cfg_override
    
    @dp.message((F.text[0] if F.text else '') != '/', flags={"long_operation": "typing"})
    async def handle_messages(message: Message):
      # if should be handled in assistant mode
      if (config.llm_assistant_use_in_chat_mode and assistant_model_available(model))\
      or (visual_mode_available(model) and parse_photo(message)):
        return await assist_message(message=message, command=SimpleNamespace(args=message.text))
      with self.queue.for_user(message.from_user.id) as available:
        if available:
          output = await self.chat(message.text, self.get_common_chat_attributes(message))
          await message.reply(text=html.quote(output))

    @dp.message(Command(commands=['reset', 'clear']), flags={"cooldown": 20})
    async def clear_llm_history(message: Message, command: Command):
      self.chatter.history[get_chat_id(message)] = []
    
    @dp.message(Command(commands=['ask', 'assist']), flags={"long_operation": "typing"})
    async def assist_message(message: Message, command: Command):
      msg = str(command.args).strip()
      if not (msg and command.args):
        return
      if not assistant_model_available(model):
        return await message.reply(text='Assistant model is not available')
      img_input = {"visual_input": await tg_image_to_data(parse_photo(message), bot)}\
                  if visual_mode_available(model) \
                  else {}
      with self.queue.for_user(message.from_user.id) as available:
        if not available:
          return
        output = await self.assist(msg, 
          self.get_common_chat_attributes(message, {'img_imput': img_input})
        )
      if config.llm_assistant_use_in_chat_mode and not hasattr(command, 'command'):
        reply = html.quote(output)
      else:
        reply = f'<b>Q</b>: {msg}\n\n<b>A</b>: {html.quote(output)}'
      await message.reply(text=(reply), allow_sending_without_reply=True)

    @dp.message(Command(commands=['llm']), flags={"cooldown": 20})
    async def helpfunction(message: Message, command: Command):
      text = f'''[LLM module].
      Commands: /ask
      Active model type: {config.llm_backend}
      Assistant mode: {str(assistant_model_available(model))} ({config.llm_assistant_chronicler})
      Character: {config.llm_character}
      Context visibility: {config.llm_history_grouping}
      Model: {model.filename if model.model else 'unknown'}
      Config: 
{json.dumps(self.chatter.gen_cfg(self.assistant_cfg_override), sort_keys=True, indent=4)}'''
      return await message.reply(text=text)