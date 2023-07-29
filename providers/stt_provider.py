from config_reader import config
from .stt import backends

active_model = backends[config.stt_backend]() if 'stt' in config.active_modules else None