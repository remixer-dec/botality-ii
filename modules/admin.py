from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from utils import parse_photo, log_exceptions
import logging
logger = logging.getLogger(__name__)


class AdminModule:
  def __init__(self, dp, bot, broker):
    @dp.message(Command(commands=["sendpic"]), flags={"admins_only": True})
    @log_exceptions(logger)
    async def send_pic(message: Message, command: CommandObject) -> None:
      photo = parse_photo(message)
      await bot.send_photo(chat_id = int(str(command.args)), photo = photo[-1].file_id)

    @dp.message(Command(commands=["delete"]), flags={"admins_only": True})
    @log_exceptions(logger)
    async def delete_msg(message: Message, command: CommandObject) -> None:
      await bot.delete_message(chat_id = message.chat.id, message_id = message.reply_to_message.message_id)
