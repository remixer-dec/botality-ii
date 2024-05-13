## Botality II  
  
This project is an implementation of a modular **telegram bot** based on [aiogram](https://github.com/aiogram/aiogram), designed for local ML Inference with remote service support. Currently integrated with:
-  **Stable Diffusion** (using [stable-diffusion-webui](https://github.com/AUTOMATIC1111/stable-diffusion-webui) API),
-  **TTS** text-to-speech engine (using [TTS (VITS)](https://github.com/coqui-ai/TTS) and [so-vits-SVC](https://github.com/svc-develop-team/so-vits-svc/tree/4.0)) as well as OS voices.  
-  **STT** integrated with multiple speech recognition engines, including [whisper.cpp](https://github.com/ggerganov/whisper.cpp)[<sup>1</sup>](https://github.com/stlukey/whispercpp.py), [whisperS2T](https://github.com/shashikg/WhisperS2T), [silero](https://github.com/snakers4/silero-models), [wav2vec2](https://ai.meta.com/blog/wav2vec-20-learning-the-structure-of-speech-from-raw-audio/)  
-  **LLMs** such as [llama (1-3)](https://github.com/facebookresearch/llama), [gpt-j](https://github.com/kingoflolz/mesh-transformer-jax#gpt-j-6b), [gpt-2](https://huggingface.co/gpt2) with support for assistant mode via instruct-tuned lora models and multimodality via [adapter-model](https://github.com/OpenGVLab/LLaMA-Adapter) 
- **TTA** experimental text-to-audio support via [audiocraft](https://github.com/facebookresearch/audiocraft)  

Accelerated LLM inference support: [llama.cpp](https://github.com/ggerganov/llama.cpp), [mlc-llm](https://github.com/mlc-ai/mlc-llm) and [llama-mps](https://github.com/remixer-dec/llama-mps/)  
Remote LLM inference support: [oobabooga/text-generation-webui](https://github.com/oobabooga/text-generation-webui/), [LostRuins/koboldcpp](https://github.com/LostRuins/koboldcpp) and [llama.cpp server](https://github.com/ggerganov/llama.cpp/tree/master/examples/server)  
Compatibility table is available [here](COMPATIBILITY.md)  
  
Evolved from predecessor [Botality I](https://github.com/remixer-dec/ru-gpt3-telegram-bot)  
Shipped with an easy-to-use webui, you can run commands and talk with the bot right in the webui.

<img src="https://i.imgur.com/cnLXvTa.png" alt="preview" height="500">

### Documentation

You can find it [here](https://github.com/remixer-dec/botality-ii/wiki/Getting-started) (coming soon)

### Changelog
Some versions have breaking changes, see [Changelog file](CHANGELOG.md) for more information

### Features
[Bot]
- User-based queues and delayed task processing
- Multiple modes to filter access scopes (WL/BL/Both/Admin-only)
- Support of accelerated inference on M1 Macs
- Memory manager, keeps track of models loaded at the same time and loads/unloads them on demand.

[LLM]
- Supports dialog mode casually playing a role described in a character file, keeping chat history with all users in group chats or with each user separately
- Character files can be easily localized for any language for non-english models
- Assistant mode via /ask command or with direct replies (configurable)
- Single-reply short-term memory for assistant feedback
- Supports visual question answering, when multimodal-adapter is available

[SD]
- CLI-like way to pass stable diffusion parameters
- pre-defined prompt wrappers
- lora integration with easy syntax: lora_name100 => &lt;lora:lora_name:1.0&gt; and custom lora activators

[TTS]
- can be run remotely, or on the same machine
- tts output is sent as voice messages
- can be used on voice messages (speech and acapella songs) to dub them with a different voice 

[STT]
- can be activated as a speech recognition tool via /stt command replying to voice messages  
- if `stt_autoreply_mode` parameter is not `none`, it recognizes voice messages and replies to them with LLM and TTS modules  

[TTA]
- can be used with /sfx and /music commands after adding `tta` to `active_modules`  

<img src="https://i.imgur.com/eCEcgCc.jpg" alt="multimodality demo" title="multimodality demo" height="400">  
  
### Setup:
- copy `.env.example` file and rename the copy to `.env`, do NOT add the .env file to your commits! 
- set up your telegram bot token and other configuration options in `.env` file
- install requirements `pip install -r requrements.txt`
- install optional requirements if you want to use tts and tts_server `pip install -r requrements-tts.txt` and `pip install -r requrements-llm.txt` if you want to use llm, you'll probably also need a fresh version of [pytorch](https://pytorch.org/get-started/locally/). For speech-to-text run `pip install -r requrements-stt.txt`, for text-to-audio run `pip install -U git+https://git@github.com/facebookresearch/audiocraft#egg=audiocraft`
- you can continue configuration in the webui, it has helpful tips about each configuration option
- for stable diffusion module, make sure that you have webui installed and it is running with `--api` flag
- for text-to-speech module download VITS models, put their names in `tts_voices` configuration option and path to their directory in `tts_path`
- for llm module, see LLM Setup section bellow
- if you want to use webui + api, run it with `python dashboard.py`, otherwise run the bot with `python bot.py` 
  
python3.10+ is recommended, due to aiogram compatibility, if you are experiencing problems with whisper or logging, please update numpy.
### Supported language models (tested):  
#### Python/Pytorch backend  
- [original llama](https://github.com/facebookresearch/llama/blob/main/example.py) (7b version was tested on [llama-mps fork](https://github.com/remixer-dec/llama-mps/tree/multimodal-adapter) for macs), requires running the bot with `python3.10 -m torch.distributed.launch --use_env bot.py`  
assistant mode for original llama is available with [LLaMa-Adapter](https://github.com/ZrrSkywalker/LLaMA-Adapter), to use both chat and assistant mode, some changes[[1]](https://github.com/remixer-dec/llama-mps/commit/a9b319a927461e4d9b5d74789b3b4a079cb90620)[[2]](https://github.com/remixer-dec/llama-mps/commit/74e9734eefaba721d03974924d0a43175237f32c) are necessary for non-mac users.
- [hf llama](https://huggingface.co/decapoda-research/llama-7b-hf/tree/main) (tests outdated) + [alpaca-lora](https://github.com/tloen/alpaca-lora) / [ru-turbo-alpaca-lora](https://huggingface.co/IlyaGusev/llama_7b_ru_turbo_alpaca_lora)
- [gpt-2](https://huggingface.co/gpt2) (tested on [ru-gpt3](https://github.com/ai-forever/ru-gpts)), nanoGPT (tested on [minChatGPT](https://github.com/ethanyanjiali/minChatGPT) [[weights](https://huggingface.co/ethanyanjiali/minChatGPT/blob/main/final_ppo_model_gpt2medium.pt)])
- [gpt-j](https://github.com/kingoflolz/mesh-transformer-jax#gpt-j-6b) (tested on a custom model)
  
#### C++ / TVM backend  
- [llama.cpp](https://github.com/abetlen/llama-cpp-python) (tested on a lot of models)[[models]](https://huggingface.co/models?sort=downloads&search=GGUF)]
- [mlc-llm-chat](https://mlc.ai/mlc-llm/#windows-linux-mac) (tested using prebuilt binaries on demo-vicuna-v1-7b-int3 model, M1 GPU acceleration confirmed, integrated via [mlc-chatbot](https://github.com/XinyuSun/mlc-chatbot))
  
#### Remote api backend  
- [oobabooga webui](https://github.com/oobabooga/text-generation-webui/) 
- [kobold.cpp](https://github.com/LostRuins/koboldcpp/) with the same `remote_ob` backend
- [llama.cpp server](https://github.com/ggerganov/llama.cpp/tree/master/examples/server) with `remote_lcpp` llm backend option (Obsidian model w/ multimodality tested)


### LLM Setup
- Make sure that you have enough RAM / vRAM to run models.
- Download the weights (and the code if needed) for any large language model
- in .env file, make sure that `"llm"` is in `active_modules`, then set:  
`llm_paths` - change the path(s) of model(s) that you downloaded  
`llm_backend` - select from `pytorch`, `llama.cpp`, `mlc_pb`, `remote_ob`, `remote_lcpp`
`llm_python_model_type` = if you set `pytorch` in the previous option, set the model type that you want to use, it can be `gpt2`,`gptj`,`llama_orig`, `llama_hf` and `auto_hf`.  
`llm_character` = a character of your choice, from `characters` directory, for example `characters.gptj_6B_default`, character files also have prompt templates and model configuration options optimal to specific model, feel free to change the character files, edit their personality and use with other models.  
`llm_assistant_chronicler` = a input/output formatter/parser for assistant task, can be `instruct` or `raw`, do not change if you do not use `mlc_pb`.  
`llm_history_grouping` = `user` to store history with each user separately or `chat` to store group chat history with all users in that chat  
`llm_assistant_use_in_chat_mode` = `True`/`False` when False, use /ask command to ask the model questions without any input history, when True, all messages are treated as questions.  
  
- For llama.cpp: make sure that you have a c++ compiler, then put all necessary flags to enable GPU support, and install it `pip install llama-cpp-python`, download model weights and change the path in `llm_paths`.
- For mlc-llm, follow the installation instructions from the docs, then clone [mlc-chatbot](https://github.com/XinyuSun/mlc-chatbot), and put 3 paths in `llm_paths`. Use with `llm_assistant_use_in_chat_mode=True` and with `raw` chronicler.  
- For oobabooga webui and kobold.cpp, instead of specifying `llm_paths`, set `llm_host`, set `llm_active_model_type` to `remote_ob` and set the `llm_character` to one that has the same prompt format / preset as your model. Run the server with --api flag.
- For llama.cpp c-server, start the `./server`, set its URL in `llm_host` and set `llm_active_model_type` to `remote_lcpp`, for multimodality please refer to this [thread](https://www.reddit.com/r/LocalLLaMA/comments/17jus3h/obsidian_worlds_first_3b_multimodal_opensource_llm/)
  
  
### Bot commands
Send a message to your bot with the command **/tti -h** for more info on how to use stable diffusion in the bot, and **/tts -h** for tts module. The bot uses the same commands as voice names in configuration file for tts. Try **/llm** command for llm module details. LLM defaults to chat mode for models that support it, assistant can be called with /ask command
  
License: the code of this project is currently distributed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) license, third party libraries might have different licenses.