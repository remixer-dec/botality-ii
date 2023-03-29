from pydantic import BaseSettings, SecretStr, validator
from typing import List, Literal, Dict

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
    llm_queue_size_per_user: int
    llm_active_model_type: Literal["gpt2","gptj","llama_orig", "llama_hf"]
    llm_paths: Dict
    llm_character: str
    llm_history_grouping: Literal["user", "chat"]
    llm_max_history_items: int
    llm_generation_cfg_override: Dict
    llm_assistant_cfg_override: Dict
    llm_assistant_chronicler: Literal["minchatgpt", "alpaca"]
    llm_assistant_use_in_chat_mode: bool
    
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
    
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

config = Settings()
