import torch
import torchaudio
from providers.stt.abstract_stt import AbstractSTT
from config_reader import config
from concurrent.futures import ThreadPoolExecutor
import asyncio
from glob import glob
from misc.memory_manager import mload

device = torch.device('cpu')

class SileroSTT(AbstractSTT):
  def __init__(self):
    if config.mm_preload_models_on_start:
      mload('st-wav2vec2', self.load, None)

  def load(self):
    model, decoder, utils = torch.hub.load(
      repo_or_dir='snakers4/silero-models',
      model='silero_stt',
      language=config.stt_model_path_or_name if len(config.stt_model_path_or_name) == 2 else 'en',
      device=device
    )
    return model, utils, decoder
  
  def stt(self, path):
    model, utils, decoder = mload('st-silero', self.load, None)
    read_batch, split_into_batches, read_audio, prepare_model_input = utils
    test_files = glob(path)
    batches = split_into_batches(test_files, batch_size=10)
    input = prepare_model_input(read_batch(batches[0]), device=device)
    output = model(input)
    transcript = '. '.join([decoder(x.cpu()) for x in output])
    print(transcript)
    return transcript
  
  async def recognize(self, audio_path):
    try:
      with ThreadPoolExecutor():
        text = await asyncio.to_thread(self.stt, audio_path)
      return False, text
    except Exception as e:
      return str(e), None 

init = SileroSTT