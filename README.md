## Multibot  
  
This project is an implementation of a modular **telegram bot** based on [aiogram](https://github.com/aiogram/aiogram), designed for remote and local ML Inference. Currently integrated with **Stable Diffusion** (using [stable-diffusion-webui](https://github.com/AUTOMATIC1111/stable-diffusion-webui) API), and **VITS** text-to-speech engine (using [TTS](https://github.com/coqui-ai/TTS)).  

### Setup:
- rename `.env.example` to `.env`
- set up your telegram bot token and other configuration options
- install requirements `pip install -r requrements.txt`
- install optional requirements if you want to use tts and tts_server `pip install -r requrements-optional.txt`
- make sure that you have webui installed for stable diffusion module and it is running with `--api` flag, and tts is set up with all the models for text-to-speech module
- run the bot with `python bot.py`  
  
python3.10+ is recommended, due to aiogram compatibility  
  
### Features
- CLI-like way to pass stable diffusion parameters
- pre-defined prompt wrappers
- lora support with easy syntax: lora_name100 => &lt;lora:lora_name:1.0&gt;
- user-based queues and delayed task processing
- multiple modes to filter access scopes
- tts output is sent as voice messages
  
### Bot commands
Send a message to your bot with the command **/tti -h** for more info on how to use stable diffusion in the bot, and **/tts -h** for tts module. The bot uses the same commands as voice names in configuration file for tts.