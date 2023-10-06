from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from utils import parse_photo, log_exceptions
from config_reader import config
import logging
logger = logging.getLogger(__name__)


class AdminModule:
  def __init__(self, dp, bot):
    @dp.message(Command(commands=["sendpic"]), flags={"admins_only": True})
    @log_exceptions(logger)
    async def send_pic(message: Message, command: CommandObject) -> None:
      photo = parse_photo(message)
      await bot.send_photo(chat_id = int(str(command.args)), photo = photo[-1].file_id)

    @dp.message(Command(commands=["delete"]), flags={"admins_only": True})
    @log_exceptions(logger)
    async def delete_msg(message: Message, command: CommandObject) -> None:
      await bot.delete_message(chat_id = message.chat.id, message_id = message.reply_to_message.message_id)

    @dp.message(Command(commands=["info"]), flags={"admins_only": True})
    async def chat_info(message: Message, command: CommandObject) -> None:
      msg = message if not message.reply_to_message else message.reply_to_message
      prefix = '[reply info]\n' if message.reply_to_message else ''
      await message.reply(f'{prefix}Chat ID: {msg.chat.id}\nUser ID: {msg.from_user.id}')
    
    @dp.message(Command(commands=["ban", "unban"]), flags={"admins_only": True})
    @log_exceptions(logger)
    async def ban_unban_user(message: Message, command: CommandObject) -> None:
      user = False
      if message.reply_to_message:
        user = message.reply_to_message.from_user
        user_id = user.id
      else:
        try:
          user_id = int(str(command.args))
        except Exception:
          return await message.reply('Incorrect user id')
      if command.command == "ban":
        if user_id == bot._me.id:
          return await message.reply('Funny!')
        if user_id in config.adminlist:
          return await message.reply('Unable ban an admin')
        if user_id not in config.blacklist:
          config.blacklist.append(user_id)
          config.blacklist = config.blacklist
          who = str(user_id) if not user else user.first_name + f" ({str(user_id)})"
          await message.reply(f'{who} has been banned')
        else:
          await message.reply('User is already banned')          
      else:
        if user_id in config.blacklist:
          config.blacklist.remove(user_id)
          config.blacklist = config.blacklist
          await message.reply('User unbanned')
        else:
          await message.reply('User is not banned')