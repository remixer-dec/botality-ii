from pydantic import BaseSettings, SecretStr, validator
from typing import List, Dict
from typing_extensions import Literal

class Settings(BaseSettings):
  bot_token: SecretStr
  adminlist: List[int]
  whitelist: List[int]
  blacklist: List[int]
  ignore_mode: Literal["blacklist", "whitelist", "both"]
  active_modules: List[str]
  apply_mps_fixes: bool
  tts_path: str
  tts_voices: List[str]
  tts_mode: Literal["local", "localhttp", "remote"]
  tts_replacements: Dict
  tts_credits: str
  tts_ffmpeg_path: str
  tts_enable_so_vits_svc: bool
  tts_so_vits_svc_code_path: str
  tts_so_vits_svc_base_tts_provider: Literal["say_macos", "built_in"]
  tts_so_vits_svc_voices: List[Dict]
  tts_queue_size_per_user: int
  tts_host: str
  sd_host: str
  sd_max_steps: int
  sd_max_resolution: int
  sd_available_samplers: List[str]
  sd_extra_prompt: str
  sd_extra_negative_prompt: str
  sd_default_sampler: str
  sd_default_n_iter: int
  sd_default_width: int
  sd_default_height: int
  sd_default_tti_steps: int
  sd_default_tti_cfg_scale: int
  sd_default_iti_cfg_scale: int
  sd_default_iti_steps: int
  sd_default_iti_denoising_strength: float
  sd_available_loras: List[str]
  sd_lora_custom_activations: Dict
  sd_only_admins_can_change_models: bool
  sd_queue_size_per_user: int
  llm_ob_host: str
  llm_queue_size_per_user: int
  llm_active_model_type: Literal["gpt2","gptj", "cerebras_gpt","llama_orig", "llama_hf", "llama_cpp", "mlc_pb", "remote_ob"]
  llm_paths: Dict
  llm_character: str
  llm_history_grouping: Literal["user", "chat"]
  llm_max_history_items: int
  llm_generation_cfg_override: Dict
  llm_assistant_cfg_override: Dict
  llm_assistant_chronicler: Literal["minchatgpt", "alpaca", "gpt4all", "raw"]
  llm_assistant_use_in_chat_mode: bool
  llm_force_assistant_for_unsupported_models: bool
  llm_max_tokens: int
  llm_max_assistant_tokens: int
  
  @validator('sd_max_resolution', 'sd_default_width', 'sd_default_height')
  def resolution_in_correct_ranges(cls, v):
    if v % 64 != 0 or v < 256 or v > 2048:
      raise ValueError('incorrect value')
    return v
  
  @validator('sd_lora_custom_activations')
  def no_lora_conflicts(cls, v, values):
    for key in v:
      try:
        assert key not in values['sd_available_loras']
      except AssertionError as e:
        e.args += ('Custom activation loras should not be listed with the same name as regular loras',)
        raise
    return v
  
  @validator('tts_so_vits_svc_voices')
  def base_voices_exist(cls, v, values):
    if not values['tts_enable_so_vits_svc']:
      return v
    for item in v:
      provider = item.get('provider', values['tts_so_vits_svc_base_tts_provider'])
      if provider == 'built_in':
        if item['base_voice'] not in values['tts_voices']:
          raise ValueError(f'base tts voice ({item["base_voice"]}) does not exist')
    return v
  
  class Config:
    env_file = '.env'
    env_file_encoding = 'utf-8'

config = Settings()
