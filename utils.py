from io import BytesIO
import base64
import argparse
import functools
import sys
import json

async def tg_image_to_data(photo, bot):
  if not photo:
    return None
  file_bytes = BytesIO()
  file_path = (await bot.get_file(file_id=photo[-1].file_id)).file_path
  await bot.download_file(file_path, file_bytes)
  image = 'data:image/png;base64,' + str(base64.b64encode(file_bytes.getvalue()), 'utf-8')
  return image

def b64_to_img(imgstr):
  from PIL import Image
  decoded = base64.b64decode(imgstr.split(',')[1])
  return Image.open(BytesIO(decoded))

# do not sysexit on error
class CustomArgumentParser(argparse.ArgumentParser):
  def error(self, message):
    raise Exception(message)

# prevents excessive line-breaks
class CustomHelpFormatter(argparse.HelpFormatter):
  def __init__(self, *args, **kwargs):
    kwargs["max_help_position"] = 24
    kwargs["width"] = 245
    super().__init__(*args, **kwargs)

# join the rest of the arguments, so they can be validated
class JoinNargsAction(argparse.Action):
  def __call__(self, parser, namespace, values, option_string=None):
    setattr(namespace, self.dest, ' '.join(values))


def parse_photo(message):
  if message.photo:
    return message.photo
  if message.document and message.document.mime_type.startswith('image'):
    return [message.document]
  if message.reply_to_message:
    if message.reply_to_message.photo:
      return message.reply_to_message.photo
    if message.reply_to_message.document and message.reply_to_message.document.mime_type.startswith('image'):
      return [message.reply_to_message.document]
  return None

def log_exceptions(logger):
  def decorator(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
      try:
        result = await func(*args, **kwargs)
        return result
      except Exception as e:
        logger.error(f"Error in {func.__name__}: {str(e)}")
    return wrapper
  return decorator

def cprint(*args, color='default'):
  keys = ['default', 'red', 'green', 'yellow', 'blue']
  sys.stdout.write(f'\x1b[1;3{keys.index(color)}m' + ' '.join(args) + '\x1b[0m\n')

def update_env(path, key, value):
  with open(path, "r") as file:
    lines = file.readlines()
  with open(path, "w+") as file:
    to_write = []
    multiline = False
    try:
      for line in lines:
        if line.replace(' ','').startswith(key + "="):
          multiline = line.replace(' ','').startswith(key + "='") and not line.endswith(("'", "'\n","'\r\n",))
          if not multiline:
            if type(value) in (dict, list):
              value = json.dumps(value)
            to_write.append(f"{key}={value}\n")
          else:
            if isinstance(value, str):
              value = json.loads(value)
            to_write.append(f"{key}='{json.dumps(value, indent=2, sort_keys=True)}'\n")
          continue
        if multiline:
          if line.endswith(("'", "'\n","'\r\n",)):
            multiline = False
          continue
        to_write.append(line)
      file.writelines(to_write)
    except Exception as e:
      file.writelines(lines)
      cprint("Unable to update .env file: " + str(e), color='red')
      raise Exception(e)

async def download_audio(bot, file_id, dl_path):
  file_path = (await bot.get_file(file_id=file_id)).file_path
  await bot.download_file(file_path, dl_path)