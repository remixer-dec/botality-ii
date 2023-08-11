import torch
import torchaudio
from transformers import SpeechEncoderDecoderModel, Wav2Vec2Processor
from providers.stt.abstract_stt import AbstractSTT
from config_reader import config
from concurrent.futures import ThreadPoolExecutor
from misc.memory_manager import mload
import asyncio

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class Wav2Vec2(AbstractSTT): 
  def __init__(self):
    if config.mm_preload_models_on_start:
      mload('st-wav2vec2', self.load, None)

  def load(self):
    processor = Wav2Vec2Processor.from_pretrained(config.stt_model_path_or_name)
    model = SpeechEncoderDecoderModel.from_pretrained(config.stt_model_path_or_name)
    if device != 'cpu':
      model = model.to(device)
      processor = processor
    return (model, processor)
  
  def stt(self, path):
    model, processor = mload('st-wav2vec2', self.load, None)
    waveform, sample_rate = torchaudio.load(path, normalize=True)
    if waveform.shape[0] == 2:
        waveform = torch.mean(waveform, dim=0)
    if sample_rate != 16000:
        resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)
        waveform = resampler(waveform)
    waveform = waveform.squeeze()
    processed = processor(waveform, sampling_rate=16_000,
                      return_tensors="pt", padding='longest', device=device)
    if device != 'cpu':
      processed['input_values'] = processed['input_values'].to(device)
      processed['attention_mask'] = processed['attention_mask'].to(device)
    print(processed)
    with torch.no_grad():
      predicted_ids = model.generate(**processed)
    
    predicted_sentences = processor.batch_decode(
        predicted_ids,
        num_processes=8,
        skip_special_tokens=True
    )
    print(predicted_sentences)
    return ' '.join(predicted_sentences)

  async def recognize(self, audio_path):
    try:
      with ThreadPoolExecutor():
        text = await asyncio.to_thread(self.stt, audio_path)
      return False, text
    except AssertionError as e:
      print(e)
      return str(e), None 

init = Wav2Vec2