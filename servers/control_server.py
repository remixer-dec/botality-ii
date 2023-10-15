from fastapi import FastAPI, Request, Response, status, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import config_reader
from bot import main, config
from servers.common import add_common_endpoints, VirtualRouter
import httpx
import multiprocessing
import os
import importlib

bot_instance = None
app = FastAPI(title='Botality WebUI')

vrouter = VirtualRouter()
add_common_endpoints(vrouter, lambda: config)

@app.post("/api/bot/{action}")
def bot_action(action):
  global bot_instance
  if not bot_instance and action == 'start':
    bot_instance = multiprocessing.Process(target=main, kwargs={"api": True})
    bot_instance.start()
  elif bot_instance and action == 'stop':
    bot_instance.terminate()
    bot_instance = None
  else:
    return {"error": "Unknown or unavailable action"}
  return {"response": "ok"}

@app.get("/api/bot/status")
async def bot_status():
  return {"response": {"running": bot_instance is not None}}

@app.get("/api/bot/env")
async def env_files():
  env_files = ['.env']
  if os.path.exists('env') and os.path.isdir('env'):
    env_files = [*env_files, *[x for x in os.listdir('env') if x.endswith('.env')]]
  active = os.environ.get('BOTALITY_ENV_FILE', '.env')
  active = os.path.basename(active)
  return {"response": {"active": active, "all": env_files}}

@app.put("/api/bot/env")
async def set_env(filename: str = Body(...)):
  global config
  if (os.path.exists('env') and os.path.isdir('env') and filename in os.listdir('env')) or filename == '.env':
    os.environ['BOTALITY_ENV_FILE'] = os.path.join('env', filename) if filename != '.env' else '.env'
    config = importlib.reload(config_reader).config
    return {"response": 'ok'}
  return {"error": 'file not found'}

@app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def redirect_request(path: str, request: Request, response: Response):
  if bot_instance:
    redirect_url = f'{config.sys_api_host}/{path}'
    try:
      async with httpx.AsyncClient() as client:
        headers = dict(request.headers)
        headers.pop('content-length', None)
        headers.pop('host', None)
        headers['content-type'] = 'application/json'
        _json = await request.json() if request.method != 'GET' else None
        redirect_response = await client.request(request.method, redirect_url, headers=headers, json=_json, timeout=config.sys_request_timeout)
      return redirect_response.json()
    except Exception:
      return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content={"error": "SERVICE UNAVAILABLE"})
  else:
    return await vrouter.run('/' + path, request.method, ((await request.json()) if request.method != 'GET' else None))

@app.on_event("startup")
def startup_event():
  print("Botality WebUI server is running on", config.sys_webui_host)

app.mount("/", StaticFiles(directory="static", html=True), name="static")

@app.exception_handler(404)
async def not_found_handler(a, b):
  return FileResponse("static/index.html", status_code=200)

def serve():
  import uvicorn
  [protocol, slash2_host, port] = config.sys_webui_host.split(':')
  if (os.environ.get('BOTALITY_AUTOSTART', '') == 'True'):
    bot_action('start')
  uvicorn.run(app, 
    host=slash2_host[2:], 
    port=int(port), 
    timeout_keep_alive=config.sys_request_timeout,
    log_level=config.sys_api_log_level
  )

if __name__ == '__main__':
  serve()