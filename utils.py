from io import BytesIO
import base64
import argparse

async def tg_image_to_data(photo, bot):
  file_bytes = BytesIO()
  file_path = (await bot.get_file(file_id=photo[-1].file_id)).file_path
  file = await bot.download_file(file_path, file_bytes)
  image = 'data:image/png;base64,' + str(base64.b64encode(file_bytes.getvalue()), 'utf-8')
  return image

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
