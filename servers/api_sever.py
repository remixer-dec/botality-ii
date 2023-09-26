import contextlib
import time
import threading
import uvicorn
from fastapi import FastAPI
from config_reader import config
from servers.common import add_common_endpoints

app = FastAPI(title='Botality API')
dispatcher = None
bot = None

add_common_endpoints(app)

@app.get("/ping")
async def ping():
  return {"response": "ok"}

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
  serverConfig = uvicorn.Config(app, host=slash2_host[2:], port=int(port), log_level="info")
  api_server = Server(config=serverConfig)
  return api_server