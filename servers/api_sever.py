import contextlib
import time
import threading
import uvicorn
from typing import Dict
from fastapi import FastAPI, Body
from config_reader import config
from servers.common import add_common_endpoints
from misc.botless_layer import handle_message

app = FastAPI(title='Botality API')
dispatcher = None
bot = None

add_common_endpoints(app)

@app.get("/ping")
async def ping():
  return {"response": "ok"}


@app.post("/chat",)
async def message(data: Dict = Body):
  reply_future = await handle_message(data, dispatcher)
  await reply_future
  return reply_future.result()

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

def init_api_server(dp):
  global dispatcher
  dispatcher = dp
  [protocol, slash2_host, port] = config.sys_api_host.split(':')
  serverConfig = uvicorn.Config(app, host=slash2_host[2:], port=int(port), log_level="info", timeout_keep_alive=120)
  api_server = Server(config=serverConfig)
  return api_server