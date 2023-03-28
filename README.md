## Botality II  
  
This project is an implementation of a modular **telegram bot** based on [aiogram](https://github.com/aiogram/aiogram), designed for remote and local ML Inference. Currently integrated with:
-  **Stable Diffusion** (using [stable-diffusion-webui](https://github.com/AUTOMATIC1111/stable-diffusion-webui) API),
-  **VITS** text-to-speech engine (using [TTS](https://github.com/coqui-ai/TTS)).  
-  **LLMs** such as **[llama](https://github.com/facebookresearch/llama)**, **[gpt-j-6b](https://github.com/kingoflolz/mesh-transformer-jax#gpt-j-6b)**, **[gpt-2](https://huggingface.co/gpt2)** with support for assistant mode via [alpaca-lora](https://github.com/tloen/alpaca-lora)  
  
evolved from predecessor [Botality I](https://github.com/remixer-dec/ru-gpt3-telegram-bot)  

### Features
[Bot]
- User-based queues and delayed task processing
- Multiple modes to filter access scopes (WL/BL/Both/Admin-only)

[LLM]
- Supports dialog mode casually playing a role described in a character file, keeping chat history with all users in group chats or with each user separately
- Character files can be easily localized for any language for non-english models
- Assistant mode

[SD]
- CLI-like way to pass stable diffusion parameters
- pre-defined prompt wrappers
- lora integration with easy syntax: lora_name100 => &lt;lora:lora_name:1.0&gt; and custom lora activators

[TTS]
- can be run remotely, or on the same machine
- tts output is sent as voice messages
  
### Setup:
- rename `.env.example` to `.env`, and do NOT add the .env file to your commits! 
- set up your telegram bot token and other configuration options
- install requirements `pip install -r requrements.txt`
- install optional requirements if you want to use tts and tts_server `pip install -r requrements-tts.txt` and `pip install -r requrements-llm.txt` if you want to use llm, you'll probably also need a fresh version of [pytorch](https://pytorch.org/get-started/locally/).
- for stable diffusion module, make sure that you have webui installed and it is running with `--api` flag
- for text-to-speech module download VITS models, put their names in `tts_voices` configuration option and path to their directory in `tts_path`
- for llm module, see LLM Setup section bellow
- run the bot with `python bot.py`  
  
python3.10+ is recommended, due to aiogram compatibility  
### Supported language models (tested): 

- [original llama](https://github.com/facebookresearch/llama/blob/main/example.py) (7b version was tested on [llama-mps fork](https://github.com/remixer-dec/llama-mps) for macs), requires running the bot with `python3.10 -m torch.distributed.launch --use_env bot.py`
- [hf llama](https://huggingface.co/decapoda-research/llama-7b-hf/tree/main) by decapoda-research (outputs are way worse than original llama on mac) + [alpaca-lora](https://github.com/tloen/alpaca-lora) (outputs are ok)
- [gpt-2](https://huggingface.co/gpt2) (tested on [ru-gpt3](https://github.com/ai-forever/ru-gpts))

- [gpt-j](https://github.com/kingoflolz/mesh-transformer-jax#gpt-j-6b) (tested on a custom model)

### LLM Setup
- Download weights (and code if needed) for a specific large language model
- in .env file set:  
`llm_paths` - change the path(s) of model(s) that you downloaded  
`llm_active_model_name` = model type that you want to use, it can be `gpt2`,`gptj`,`llama_orig`  
`llm_character` = a character of your choice, from `characters` directory, for example `characters.gptj_6B_default`, character files also have model configuration options optimal to specific model, feel free to change the character files and use with other models.  
`llm_history_grouping` = `user` to store history with each user separately or `chat` to store group chat history with all users in that chat  
`llm_assistant_use_in_chat_mode` = `True`/`False` when False, use /ask command to use alpaca-lora in assistant mode, when True, all messages are treated as questions.
  
  
### Bot commands
Send a message to your bot with the command **/tti -h** for more info on how to use stable diffusion in the bot, and **/tts -h** for tts module. The bot uses the same commands as voice names in configuration file for tts.