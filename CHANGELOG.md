## v0.6
- Migrated to `aiogram==3.1.1`, `pydantic==2.4.0`, if you want to keep old pydantic, use `aiogram==3.0.0b7`.
- WebUI made with Vue is available! Run it with `dashboard.py`
- Configuration preset switching in WebUI, to change path of default .env file, use `--env` on `dashboard.py`, additional configuration files should are stored with .env extension in env directory.
- New configuration options: `sys_webui_host`, `sys_api_host`, `sys_request_timeout`, `sys_api_log_level`
- Fixed TTS initialization failing when threaded mode was off
- Fixed memory manager initialization
- For model configuration UI the `path_to_llama_cpp_weights_dir` key has been added to `llm_paths`
- Reply context (1-step memory) can now be toggled with `llm_assistant_add_reply_context` option
- Configuration hints are available in the WebUI.
- Model manager in the WebUI can be used to download and set up models. A few types of models are initially supported.

## v0.5  
- full TTS refactoring  
- universal cross-platform os TTS provider (pyttsx4) support  
- threaded initialization (configurable via `threaded_initialization` option)  
- bugfixes

### Breaking changes  
- `tts_enable_so_vits_svc` config option has been removed in favor of `tts_enable_backends`.  
- `tts_so_vits_svc_base_tts_provider` config option has been removed, you only need base voice from now on.  


## v0.4
- so-vits-svc-4.1 support
- experimental memory manager (now supports all models except LLMs with pytorch backend)

### Breaking changes
- `tts_so_vits_svc_code_path` config option has been renamed to `tts_so_vits_svc_4_0_code_path`, and `tts_so_vits_svc_4_1_code_path` option was added to support so-vits-svc-4.1 models, to specify that the model is a 4.1 mode, use "v": 4.1 in `tts_so_vits_svc_voices`.
- `llm_host` has ben fixed in .env.example file, `llm_ob_host` has been removed


## v0.3
- Basic config state reactivity (runtime config changes in bot are reflected in .env)
- Fixed SD model info retrieval and reinitialization
- Global module accessibility milestone 2
- Experimental multi-line dialog answer support
- Speech-to-text via Whisper.cpp, Silero an Wav2Vec2
- Seamless dialog mode voice->text->llm->voice
- Text-to-audio via Audiocraft

## v0.2
- LLM module / provider refactoring
- Reply chronicler with single-item history
- Kobold.cpp and llama.cpp server support
- SD Lora API support
- Global module accessibility milestone 1

### Breaking changes
* `MinChatGPTChronicler` and `GPT4AllChronicler` were removed
Default assistant chronicler becomes `instruct`, `alpaca` name is kept for a limited time for backwards compatibility  
* `llm_ob_host` has been renamed to `llm_host`
* `llm_active_model_type` has been deprecated and replaced by two new keys: `llm_backend` and `llm_python_model_type` (when backend is pytorch)
* In `llm_python_model_type` option `cerebras_gpt` has been renamed to `auto_hf`
* `path_to_cerebras_weights` has been renamed to `path_to_autohf_weights`
* `sd_available_loras` has been deprecated, lora API endpoint is used

## v0.1 
* initial version with incremental changes and full backwards compatibility with previous commits