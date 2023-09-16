from collections import OrderedDict

from providers.tts.say_macos import Say
from providers.tts.coqui_tts import CoquiTTS
from providers.tts.py_ttsx4 import TTSx4
from providers.tts.so_vits_svc import SoVitsSVC

from providers.tts.remote_tts import RemoteTTS

tts_backends = OrderedDict()
tts_backends['say_macos'] = Say
tts_backends['ttsx4'] = TTSx4
tts_backends['coqui_tts'] = CoquiTTS
tts_backends['so_vits_svc'] = SoVitsSVC