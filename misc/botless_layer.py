from aiogram.types import Message, Chat, User
from aiogram.filters import Command
from asyncio import Future
from types import SimpleNamespace


class CommandRegistrationHijacker:
  'Creates map: command -> get_handler in dp.command_map and [[magic_filter, get_handler], ...] in dp.filter_arr'
  def __init__(self, dp):
    self.orig_msg_handler = dp.message
    self.dp = dp
    dp.comamnd_map = {}
    dp.filter_arr = []
    dp.message = self.hijacked_message_decorator

  def hijacked_message_decorator(self, *args, **kwargs):
    handler = None
    if len(args) > 0:
      if type(args[0].commands) is tuple:
        prefix = args[0].prefix
        for command in args[0].commands:
          self.dp.comamnd_map[prefix + command] = lambda: handler
      else:
        self.dp.filter_arr.append([args[0], lambda: handler])

    decorated = self.orig_msg_handler(*args, **kwargs)
    def dec_wrapper(*args, **kwargs):
      nonlocal handler
      if len(args) > 0:
        handler = args[0]
      return decorated(*args, **kwargs)
    return dec_wrapper

class EmulatedMessage(Message):
  def __init__(self, reply_hijacker, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.__reply_hijacker = reply_hijacker
  async def reply(self, *args, **kwargs):
    return await self.__reply_hijacker(*args, **kwargs)
  async def answer(self, *args, **kwargs):
    return await self.__reply_hijacker(*args, **kwargs)

def getHijackerAndFuture():
  reply_future = Future()
  async def reply_hijack(text, *args, **kwargs):
    reply_future.set_result({"response": {"text": text}})
  return reply_hijack, reply_future

async def handle_message(data, dp):
  text = data.get('text')
  command = Command.extract_command(None, text)
  handler = dp.comamnd_map.get(command.prefix + command.command, None)
  reply_hijack, reply_future = getHijackerAndFuture()
  user = User(id=1, is_bot=False, first_name='Admin', last_name='Local')
  message = EmulatedMessage(reply_hijack, message_id=-1, date=0, chat=Chat(id=0, type='local'), from_user=user, text=text)
  if not handler:
    for magic_filter, get_handler in dp.filter_arr:
      if magic_filter.resolve(message):
        await get_handler()(message=message)
  else:
    handler = handler()
    await handler(message=message, command=command)
  return reply_future
    
