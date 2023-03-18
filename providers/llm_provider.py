from config_reader import config
from .llm import ll_models

active_model = ll_models[config.llm_active_model_name]() if 'llm' in config.active_modules else None
