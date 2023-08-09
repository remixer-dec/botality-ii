## v0.4
- so-vits-svc-4.1 support

### Breaking changes
- `tts_so_vits_svc_code_path` config option has been renamed to `tts_so_vits_svc_4_0_code_path`, and `tts_so_vits_svc_4_1_code_path` option was added to support so-vits-svc-4.1 models, to specify that the model is a 4.1 mode, use "v": 4.1 in `tts_so_vits_svc_voices`.


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