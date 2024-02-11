import importlib
whispercpp = lambda: importlib.import_module('providers.stt.whisper')
silero = lambda: importlib.import_module('providers.stt.silero')
wav2vec2 = lambda: importlib.import_module('providers.stt.wav2vec2')
whisperS2T = lambda: importlib.import_module('providers.stt.whisperS2T')

backends = {
  'whisper': whispercpp,
  'silero': silero,
  'wav2vec2': wav2vec2,
  'whisperS2T_CTranslate2': whisperS2T,
  'whisperS2T_TensorRT-LLM': whisperS2T
}