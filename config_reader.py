from pydantic import SecretStr, validator, constr
try:
  from pydantic_settings import BaseSettings
except ImportError:
  from pydantic import BaseSettings
from typing import List, Dict, Union
from typing_extensions import Literal
from utils import update_env
import os
from automigration import verify_environment


class Settings(BaseSettings):
  bot_token: SecretStr
  adminlist: List[int]
  whitelist: List[int]
  blacklist: List[int]
  ignore_mode: Literal["blacklist", "whitelist", "both"]
  active_modules: List[Literal["llm", "sd", "tts", "stt", "tta", "admin"]]
  threaded_initialization: bool
  apply_mps_fixes: bool
  tts_path: str
  tts_voices: List[Union[str, Dict]]
  tts_mode: Literal["local", "localhttp", "remote"]
  tts_replacements: Dict
  tts_credits: str
  tts_ffmpeg_path: str
  tts_enable_backends: List[Literal['say_macos', 'ttsx4', 'coqui_tts', 'so_vits_svc']]
  tts_list_system_voices: bool
  tts_so_vits_svc_4_0_code_path: str
  tts_so_vits_svc_4_1_code_path: str
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
  sd_default_iti_sampler: str
  sd_launch_process_automatically: bool
  sd_launch_command: str
  sd_launch_dir: str
  sd_launch_waittime: int
  sd_lora_custom_activations: Dict
  sd_only_admins_can_change_models: bool
  sd_queue_size_per_user: int
  llm_host: str
  llm_queue_size_per_user: int
  llm_backend: Literal ['pytorch', 'llama_cpp', 'mlc_pb', 'remote_ob', 'remote_lcpp']
  llm_python_model_type: Literal["gpt2","gptj", "auto_hf","llama_orig", "llama_hf"]
  llm_paths: Dict
  llm_character: str
  llm_history_grouping: Literal["user", "chat"]
  llm_max_history_items: int
  llm_generation_cfg_override: Dict
  llm_assistant_cfg_override: Dict
  llm_assistant_chronicler: Literal["alpaca", "instruct", "raw"]
  llm_assistant_use_in_chat_mode: bool
  llm_assistant_add_reply_context: bool
  llm_force_assistant_for_unsupported_models: bool
  llm_max_tokens: int
  llm_max_assistant_tokens: int
  llm_lcpp_gpu_layers: int
  llm_lcpp_max_context_size: int
  llm_remote_launch_process_automatically: bool
  llm_remote_launch_command: str
  llm_remote_launch_dir: str
  llm_remote_launch_waittime: int
  llm_remote_model_name: str
  stt_backend: Literal['whisper', 'silero', 'wav2vec2', 'whisperS2T_CTranslate2', 'whisperS2T_TensorRT-LLM']
  stt_model_path_or_name: str
  stt_autoreply_mode: Literal['none', 'assistant', 'chat']
  stt_autoreply_voice: str
  stt_queue_size_per_user: int
  tta_queue_size_per_user: int
  tta_device: Literal["cpu", "cuda", "mps"]
  tta_music_model: str
  tta_sfx_model: str
  tta_duration: int
  python_command: str
  mm_preload_models_on_start: bool
  mm_ram_cached_model_count_limit: int
  mm_vram_cached_model_count_limit: int
  mm_management_policy: Literal["COUNT", "MEMORY", "BOTH", "NONE"]
  mm_unload_order_policy: Literal["LEAST_USED", "OLDEST_USE_TIME", "OLDEST_LOAD_ORDER", "MEMORY_FOOTPRINT"]
  mm_autounload_after_seconds: int
  sys_webui_host: str
  sys_api_host: str
  sys_request_timeout: int
  sys_api_log_level: str
  lang: constr(min_length=2, max_length=2, to_lower=True)
  extensions_config: Dict
  
  @validator('sd_max_resolution', 'sd_default_width', 'sd_default_height', allow_reuse=True)
  def resolution_in_correct_ranges(cls, v):
    if v % 64 != 0 or v < 256 or v > 2048:
      raise ValueError('incorrect value')
    return v
  
  class Config:
    env_file = os.environ.get('BOTALITY_ENV_FILE', '.env')
    env_file_encoding = 'utf-8'
    extra='ignore'
    validate_assignment = True


# mirror all config changes to .env file
class SettingsWrapper(Settings):
  def __setattr__(self, name, value):
    if name == 'bot_token':
      raise KeyError('setting bot token dynamically is not allowed')
    super().__setattr__(name, value)
    update_env(self.Config.env_file, name, value)

verify_environment()
config = SettingsWrapper()