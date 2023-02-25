from pydantic import BaseSettings, SecretStr, validator
from typing import List, Literal, Dict

class Settings(BaseSettings):
    bot_token: SecretStr
    adminlist: List[int]
    whitelist: List[int]
    blacklist: List[int]
    ignore_mode: Literal["blacklist", "whitelist", "both"]
    active_modules: List[str]
    tts_path: str
    tts_voices: List[str]
    tts_mode: Literal["local", "localhttp", "remote"]
    tts_replacements: Dict
    tts_credits: str
    tts_ffmpeg_path: str
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
    
    @validator('sd_max_resolution', 'sd_default_width', 'sd_default_height')
    def resolution_in_correct_ranges(cls, v):
        if v % 64 != 0 or v < 256 or v > 2048:
            raise ValueError('incorrect value')
        return v
    
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

config = Settings()
