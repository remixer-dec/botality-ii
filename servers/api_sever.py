import contextlib
import time
import threading
import uvicorn
from typing import Dict
from fastapi import FastAPI, Body
from fastapi.responses import RedirectResponse
from config_reader import config
from servers.common import add_common_endpoints
from misc.botless_layer import handle_message
from misc.memory_manager import RAM, VRAM
from misc import model_manager

app = FastAPI(title='Botality API')
dispatcher = None
bot = None

add_common_endpoints(app)

@app.on_event("startup")
def startup_event():
    print("Botality API server is running on", config.sys_api_host)

@app.get("/")
async def movetowebui():
  return RedirectResponse(url=config.sys_webui_host, status_code=301)

@app.get("/ping")
async def ping():
  return {"response": "ok"}

@app.post("/chat")
async def message(data: Dict = Body):
  reply_future = await handle_message(data, dispatcher)
  await reply_future
  return reply_future.result()

@app.get("/status")
async def status():
  return { "response": {
    "modules": list(dispatcher.modules.keys()),
    "counters": dispatcher.counters,
    "timings": dispatcher.timings,
    "memory_manager": {
      "RAM": RAM.stats(),
      "VRAM": VRAM.stats() if VRAM else None
    },
    "bot": {
      "name": bot._me.first_name,
      "username": bot._me.username,
      "can_join_groups": bot._me.can_join_groups,
      "can_read_all_group_messages": bot._me.can_read_all_group_messages
    } if bot._me else None,
    "access_mode": config.ignore_mode
  }}

@app.get("/models")
async def models():
  return {"response": model_manager.get_models()}

@app.post("/models/install/{model_type}")
async def install_models(model_type: str, body: Dict = Body):
  return model_manager.install_model(model_type, body)

@app.post("/models/uninstall/{model_type}")
async def uninstall_models(model_type: str, body: Dict = Body):
  return model_manager.uninstall_model(model_type, body)

@app.get("/models/install/{task_id}")
async def install_status(task_id: int):
  return {'response': model_manager.get_task_info(task_id)}

@app.post("/models/select/{model_type}")
async def select_model(model_type: str, body: Dict = Body):
  return model_manager.select_model(model_type, body)

@app.get("/voices")
async def voices():
  tts = dispatcher.modules.get('tts')
  if not tts:
    return {'error': 'TTS module not initialized'}
  else:
    return {'response': [{'voice': v} for v in tts.all_voices]}

class Server(uvicorn.Server):
  def install_signal_handlers(self):
    pass

  @contextlib.contextmanager
  def run_in_thread(self):
    thread = threading.Thread(target=self.run)
    thread.start()
    try:
      while not self.started:
        time.sleep(1e-3)
      yield
    finally:
      self.should_exit = True
      thread.join()

def init_api_server(dp, bot_instance):
  global dispatcher, bot
  dispatcher = dp
  bot = bot_instance
  [protocol, slash2_host, port] = config.sys_api_host.split(':')
  serverConfig = uvicorn.Config(
    app, host=slash2_host[2:], port=int(port), 
    log_level=config.sys_api_log_level, timeout_keep_alive=config.sys_request_timeout
  )
  api_server = Server(config=serverConfig)
  return api_server