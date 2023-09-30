from aiogram.types import Message, Chat, User
from aiogram.filters import Command
from asyncio import Future
from types import SimpleNamespace
import base64


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
  def __init__(self, hijacks, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.__reply_hijacker = hijacks.get('reply')
    self.__voice_hijacker = hijacks.get('voice')
    self.__photo_hijacker = hijacks.get('photo')
    self.__mediaGroup_hijacker = hijacks.get('mediaGroup')
  async def reply(self, *args, **kwargs):
    return await self.__reply_hijacker(*args, **kwargs)
  async def answer(self, *args, **kwargs):
    return await self.__reply_hijacker(*args, **kwargs)
  async def answer_voice(self, *args, **kwargs):
    return await self.__voice_hijacker(*args, **kwargs)
  async def reply_voice(self, *args, **kwargs):
    return await self.__voice_hijacker(*args, **kwargs)
  async def answer_photo(self, *args, **kwargs):
    return await self.__photo_hijacker(*args, **kwargs)
  async def reply_photo(self, *args, **kwargs):
    return await self.__photo_hijacker(*args, **kwargs)
  async def answer_media_group(self, *args, **kwargs):
    return await self.__mediaGroup_hijacker(*args, **kwargs)
  async def reply_media_group(self, *args, **kwargs):
    return await self.__mediaGroup_hijacker(*args, **kwargs)


def getHijackerAndFuture():
  reply_future = Future()
  async def reply(text, *args, **kwargs):
    reply_future.set_result({"response": {"text": text}})
  async def sendVoice(voice, message_thread_id=None, caption=None, *args, **kwargs):
    reply_future.set_result({"response": {"voice": base64.b64encode(voice.data), "text": caption}})
  async def sendPhoto(input_file, caption=None, *args, **kwargs):
    reply_future.set_result({"response": {"photos": [base64.b64encode(input_file.data)], "text": caption}})
  async def sendMediaGroup(media, *args, **kwargs):
    images = []
    captions = []
    # only supports images for now
    for m in media:
      images.append(base64.b64encode(m.media.data))
      if m.caption:
        captions.append(m.caption)
    reply_future.set_result({"response": {"photos": images, "text": '\n'.join(captions)}})
  hijacks = {'reply': reply, 'voice': sendVoice, 'photo': sendPhoto, 'mediaGroup': sendMediaGroup}
  return hijacks, reply_future

async def handle_message(data, dp):
  text = data.get('text')
  command = Command.extract_command(None, text)
  handler = dp.comamnd_map.get(command.prefix + command.command, None)
  hijacks, reply_future = getHijackerAndFuture()
  user = User(id=1, is_bot=False, first_name='Admin', last_name='')
  message = EmulatedMessage(hijacks, message_id=-1, date=0, chat=Chat(id=0, type='local'), from_user=user, text=text)
  if not handler:
    for magic_filter, get_handler in dp.filter_arr:
      if magic_filter.resolve(message):
        handler = get_handler()
        await handler(message=message)
    if not handler:
      reply_future.set_result({'response': {"text": 'Command not found'}})
  else:
    handler = handler()
    await handler(message=message, command=command)
  return reply_future
    
