from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from utils import parse_photo, log_exceptions
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
