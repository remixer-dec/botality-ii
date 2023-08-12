
from aiogram import html, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, BufferedInputFile, InputMediaPhoto
from providers.sd_provider import tti, iti, models, embeddings, loras, switch_model, refresh_model_list
from utils import tg_image_to_data, parse_photo, CustomArgumentParser, JoinNargsAction
from custom_queue import UserLimitedQueue, semaphore_wrapper
from typing import Literal
from config_reader import config
import asyncio
import pydantic
import re
import shlex
import random

sd_available_resolutions = list(range(256, config.sd_max_resolution + 1, 64))

class SDArguments(pydantic.BaseModel):
  denoising_strength: float = pydantic.Field(None, ge=0, le=1, alias='d', description='Denoising strength')
  cfg_scale: float = pydantic.Field(None, ge=1, le=25, alias='c', description='Cfg scale')
  steps: int = pydantic.Field(None, ge=5, le=config.sd_max_steps, alias='st')
  sampler_name: Literal[tuple(config.sd_available_samplers)] = pydantic.Field(None, alias="sa", description='Sampler')
  width: Literal[tuple(sd_available_resolutions)] = pydantic.Field(None, alias="wi", description='Width')
  height: Literal[tuple(sd_available_resolutions)] = pydantic.Field(None, alias="he", description='Height')
  negative_prompt: str = pydantic.Field(None, alias='np', description='Negative prompt')
  seed: int = pydantic.Field(None, ge=-1, alias='se', description='Seed')
  prompt: str = pydantic.Field(None)
  mask: Literal[1, -1] = pydantic.Field(None, alias='ma', description='Inpaint mask')
  inpainting_fill: int = pydantic.Field(None, ge=0, le=3, alias='fi', description='Inpaint fill mode')


class StableDiffusionModule:
  def __init__(self, dp, bot):
    self.queue = UserLimitedQueue(config.sd_queue_size_per_user)
    self.semaphore = asyncio.Semaphore(1)
    if config.mm_preload_models_on_start:
      asyncio.run(refresh_model_list())

    @dp.message(Command(commands=["tti", "iti", "ttiraw", "itiraw"]), flags={"long_operation": "upload_photo"})
    async def command_sd_handler(message: Message, command: CommandObject, album=False) -> None:
      with self.queue.for_user(message.from_user.id) as available:
        if available:
          parse_error, params = self.parse_input(command.args)
          if parse_error:
            return await message.answer(f"{html.quote(parse_error)}")
          prompt = params['prompt']
          if not command.command.endswith('raw'):
            params = self.apply_standard_prompt_modifiers(params)
          processor = tti

          photo = parse_photo(message)
          if command.command.startswith("iti") and photo:
            image_data = await tg_image_to_data(photo, bot)
            params['init_images'] = [image_data]
            if 'mask' in params and album and len(album) > 1:
              if params['mask'] == -1:
                params['inpainting_mask_invert'] = 1
              params['mask'] = await tg_image_to_data(parse_photo(album[1]), bot)
            processor = iti
          elif command.command.startswith("iti"):
            return await message.answer("Error, <b>unable to find initial photo</b>")

          wrapped_runner = semaphore_wrapper(self.semaphore, processor)
          sd_error, data, details = await wrapped_runner(params)
          reply_to = message.reply_to_message.message_id if message.reply_to_message is not None else None
          
          if sd_error:
            return await message.answer(f"<b>Error:</b> {sd_error}")
          else:
            images = [InputMediaPhoto(
              type='photo', 
              media=BufferedInputFile(i, filename='image.png'), 
              caption= None if idx != 0 else (f'<pre>{html.quote(prompt[0:768])}</pre>\n' + 
              f'Seed: {details.get("seed")}\n' +
              f'Sampler: {details.get("sampler_name")}\n' +
              f'Cfg scale: {details.get("cfg_scale")}\n' + 
              f'Steps: {details.get("steps")}\n' +
              f'Model: {details.get("model")}')
            ) for idx, i in enumerate(data)]
          await message.answer_media_group(media=images, reply_to_message_id=reply_to)

    @dp.message(F.media_group_id)
    async def handle_media_groups(*args, **kwargs):
      return

    @dp.message(Command(commands=["models", "loras", "embeddings"]), flags={"cooldown": 5})
    async def list_sd_models(message: Message, command: CommandObject):
      if len(models.values()) == 0:
        await refresh_model_list()
      if command.command == "models":
        return message.answer('<b>Available models:</b> \n' + "\n".join(models.values()))
      if command.command == "embeddings":
        return message.answer('<b>Available embeddings:</b> \n' + "\n".join(embeddings))
      if command.command == "loras":
        loras_list = sorted([*loras, *config.sd_lora_custom_activations.keys()])
        return message.answer('<b>Available loras:</b> \n' + "\n".join(loras_list))

    @dp.message(
      Command(commands=["model", "changemodel", "switchmodel"]), 
      flags={
        "cooldown": 30, 
        "admins_only": config.sd_only_admins_can_change_models, 
        "long_operation":"choose_sticker"
      }
    )
    async def switch_sd_model(message: Message, command: CommandObject):
      async with self.semaphore:
        if command.args in models.values():
          success = await switch_model(command.args)
          if success:
            return message.answer(f'<b>Model changed to:</b> {command.args}')
          else:
            return message.answer('<b>Unable to change the model.</b>')
        else:
          if not command.args:
            return message.answer('use this command with model name to change the model, try /models for all model names')
          return message.answer('<b>Model not found</b>')



  def parse_input(self, user_input):
      user_input = str(user_input) + ' '
      parser = CustomArgumentParser(description='generate images from text and other images')
      parser.add_argument('-d', type=float, help='Denoising strength (for image-to-image) (0 <= d <= 1)')
      parser.add_argument('-c', type=float, help='Cfg scale (1 <= c <= 25)')
      parser.add_argument('-sa', choices=['Euler a', 'Euler', 'Heun', 'DPM++ 2M', 'DPM++ 2S a'], help='Sampler')
      parser.add_argument('-st', type=int, help=f'Number of steps (5 <= st <= {config.sd_max_steps})')
      parser.add_argument('-se', type=int, help='Seed')
      parser.add_argument('-wi', type=int, help='Image width')
      parser.add_argument('-he', type=int, help='Image height')
      parser.add_argument('-ma', type=int, help='Use the 2nd image as inpaint regular/inverse mask (1 or -1)')
      parser.add_argument('-fi', type=int, help='Inpaint mask fill mode [0 <= fi <= 3], fill/original/l.noise/l.nothing')
      parser.add_argument('-np', type=str, help='Negative prompt')
      parser.add_argument('prompt', type=str, help='prompt', nargs="*", action=JoinNargsAction)
      try:
        # override default -h behavior
        if '-help' in user_input or '—help' in user_input or '-h ' in user_input:
          return (parser.format_help().replace(
            'bot.py','/tti /iti /ttiraw /itiraw, /models /loras /embeddings /command@botname params text' 
          ), None)
        # parse arguments using custom arg parser
        args = parser.parse_args(shlex.split(user_input))
        # apply pydantic checks
        sd_args = {k: v for k, v in SDArguments(**vars(args)) if v is not None}
        return (False, sd_args)
      except (Exception, SystemExit) as e:
        return (str(e), None)

  def apply_standard_prompt_modifiers(self, params):
    params['prompt'] = config.sd_extra_prompt.format(prompt=self.parse_lora(params['prompt']))
    params['negative_prompt'] = config.sd_extra_negative_prompt.format(
      negative_prompt='' if 'negative_prompt' not in params else params['negative_prompt']
    ) 
    if 'width' in params and 'height' in params:
      if params['width'] == params['height']:
        params['prompt'] += ', square image'
    return params

  def parse_lora(self, prompt):
    if 'lora' in prompt:
      return prompt
    seamless_loras = config.sd_lora_custom_activations or {}
    for key in seamless_loras:
      if type(seamless_loras[key]) is list:
        prompt = prompt.replace(key, random.choice(seamless_loras[key]))\
                       .replace('LORA_RANGES', str(random.choice([0.9, 0.95, 1.0, 1.1, 1.2])))
      else:
        prompt = prompt.replace(key, seamless_loras[key])
    subst = "<lora:\\1:\\2.\\3\\4>"
    for lora in loras:
      regex = fr"({lora})(-?[0-9])?([0-9])([0-9])"
      prompt = re.sub(regex, subst, prompt, 1, re.IGNORECASE)
    return prompt

  async def tti(self, params):
    wrapped_runner = semaphore_wrapper(self.semaphore, tti)
    return await wrapped_runner(params)
 
  async def iti(self, params):
    wrapped_runner = semaphore_wrapper(self.semaphore, iti)
    return await wrapped_runner(params)