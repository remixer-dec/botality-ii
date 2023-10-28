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
    params = {**self.assistant.gen_cfg(self.assistant_cfg_override), **context.get('img_input', {})}
    return await self.complete_with_chronicler(text, self.assistant, context, params, config.llm_max_assistant_tokens)

  async def chat(self, text, context):
    params = self.chatter.gen_cfg(self.chat_cfg_override)
    return await self.complete_with_chronicler(text, self.chatter, context, params, config.llm_max_tokens)

  async def reply(self, text, context, message):
    params = self.assistant.gen_cfg(self.assistant_cfg_override)
    context['reply_text'] = message.reply_to_message.text
    return await self.complete_with_chronicler(text, self.replier, context, params, config.llm_max_assistant_tokens)

  async def complete_with_chronicler(self, text, chronicler, context, params, length):
    prompt = chronicler.prepare({
      "message": text, 
      "model": self.model,
      **context
    })
    wrapped_runner = semaphore_wrapper(self.semaphore, self.model.generate)
    error, result = await wrapped_runner(prompt, config.llm_max_assistant_tokens, params)
    return chronicler.parse(result, context.get('chat_id', 0), len(prompt)) if not error else str(error)

  async def complete_raw(self, text, context):
    wrapped_runner = semaphore_wrapper(self.semaphore, self.model.generate)
    error, result = await wrapped_runner(text, config.llm_max_assistant_tokens, self.assistant.gen_cfg({}))
    return result

  def should_use_reply_chronicler(self, message, bot):
    reply = message.reply_to_message
    is_reply_from_bot = reply and reply.from_user.id == bot._me.id
    is_qa_format = reply and reply.text and reply.text.startswith('Q:')
    always_assist = config.llm_assistant_use_in_chat_mode and assistant_model_available(self.model)
    return is_reply_from_bot and (is_qa_format or always_assist) and config.llm_assistant_add_reply_context

  def get_common_chat_attributes(self, message, additional=None):
    return {
      'author': message.from_user.first_name.replace(' ', '') or 'User',
      'chat_id': get_chat_id(message),
      'user_id': message.from_user.id,
      **(additional or {})
    }

  def __init__(self, dp, bot):
    self.queue = UserLimitedQueue(config.llm_queue_size_per_user)
    self.semaphore = asyncio.Semaphore(1)
    self.chatter = chroniclers['chat'](config.llm_character, False, config.llm_max_history_items)
    self.assistant = chroniclers[config.llm_assistant_chronicler](config.llm_character)
    self.replier = chroniclers['reply'](config.llm_character)
    self.model = active_model.init(config.llm_paths, self.chatter.init_cfg() or {}) 
    self.chat_cfg_override = config.llm_generation_cfg_override
    self.assistant_cfg_override = config.llm_assistant_cfg_override
    
    @dp.message((F.text[0] if F.text else '') != '/', flags={"long_operation": "typing"})
    async def handle_messages(message: Message):
      # ignore deep replies to other users
      if message.reply_to_message and message.reply_to_message.from_user.id != bot._me.id:
        return
      should_parse_reply = self.should_use_reply_chronicler(message, bot)
      # if should be handled in assistant mode
      if (config.llm_assistant_use_in_chat_mode and assistant_model_available(self.model))\
      or (visual_mode_available(self.model) and parse_photo(message)) or should_parse_reply:
        command = SimpleNamespace(args=message.text, parse_reply=should_parse_reply)
        return await assist_message(message=message, command=command)
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
      if not assistant_model_available(self.model):
        return await message.reply(text='Assistant model is not available')
      img_input = {"visual_input": await tg_image_to_data(parse_photo(message), bot)}\
                  if visual_mode_available(self.model) \
                  else {}
      with self.queue.for_user(message.from_user.id) as available:
        if not available:
          return
        if hasattr(command, 'parse_reply') and not img_input:
          output = await self.reply(msg,
            self.get_common_chat_attributes(message),
            message
          )
        else:
          output = await self.assist(msg, 
            self.get_common_chat_attributes(message, {'img_input': img_input})
          )
      if config.llm_assistant_use_in_chat_mode and not hasattr(command, 'command'):
        reply = html.quote(output)
      else:
        reply = f'<b>Q</b>: {msg}\n\n<b>A</b>: {html.quote(output)}'
      await message.reply(text=(reply), allow_sending_without_reply=True)

    @dp.message(Command(commands=['llm']), flags={"cooldown": 20})
    async def helpfunction(message: Message, command: Command):
      return await message.reply(text=self.help(dp, bot))
  
  def help(self, dp, bot):
    extra_backend_info = ''
    if config.llm_backend == 'pytorch':
      extra_backend_info = '\nModel type: '+ config.llm_python_model_type + '\n'
    text = f'''<b>[LLM module]</b>.
      Commands: /ask /llm /reset
      Active model type: {config.llm_backend}{extra_backend_info}
      Assistant mode: {str(assistant_model_available(self.model))} ({config.llm_assistant_chronicler})
      Character: {config.llm_character}
      Context visibility: {config.llm_history_grouping}
      Max new tokens: {str(config.llm_max_tokens)}
      Max new tokens (assistant): {str(config.llm_max_assistant_tokens)}
      Visual adapter: {'supported' if visual_mode_available(self.model) else 'not supported'}
      Model: {self.model.filename if hasattr(self.model, 'filename') else 'unknown'}
      Config: 
{json.dumps(self.chatter.gen_cfg(self.assistant_cfg_override), sort_keys=True, indent=4)}'''
    return text