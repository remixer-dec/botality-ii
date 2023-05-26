from io import BytesIO
import base64
import argparse
import functools

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