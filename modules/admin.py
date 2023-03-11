from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from utils import parse_photo
import logging
logger = logging.getLogger(__name__)


class AdminModule:
  def __init__(self, dp, bot, broker):
    @dp.message(Command(commands=["sendpic"]), flags={"admins_only": True})
    async def send_pic(message: Message, command: CommandObject) -> None:
      try:
        photo = parse_photo(message)
        await bot.send_photo(chat_id = int(str(command.args)), photo=photo[-1].file_id)
        return 
      except Exception as e:
        logger.error('error: ' + e)