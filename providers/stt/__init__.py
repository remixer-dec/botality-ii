import importlib
whispercpp = lambda: importlib.import_module('providers.stt.whisper')
silero = lambda: importlib.import_module('providers.stt.silero')
wav2vec2 = lambda: importlib.import_module('providers.stt.wav2vec2')

backends = {
  'whisper': whispercpp,
  'silero': silero,
  'wav2vec2': wav2vec2
}