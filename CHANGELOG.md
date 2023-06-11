## v0.2

### Breaking changes
* `MinChatGPTChronicler` and `GPT4AllChronicler` were removed
Default assistant chronicler becomes `instruct`, `alpaca` name is kept for a limited time for backwards compatibility  
* `llm_ob_host` has been renamed to `llm_host`
* `llm_active_model_type` has been deprecated and replaced by two new keys: `llm_backend` and `llm_python_model_type` (when backend is python)

## v0.1 
* initial version with incremental changes and full backwards compatibility with previous commits