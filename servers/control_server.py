from fastapi import FastAPI, Request, Response, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from bot import main, config
from servers.common import add_common_endpoints, VirtualRouter
import httpx
import multiprocessing

bot_instance = None
app = FastAPI(title='Botality WebUI')

vrouter = VirtualRouter()
add_common_endpoints(vrouter)

@app.post("/api/bot/{action}")
async def start_bot(action):
  global bot_instance
  if not bot_instance and action == 'start':
    bot_instance = multiprocessing.Process(target=main)
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
        redirect_response = await client.request(request.method, redirect_url, headers=headers, json=_json)
      return redirect_response.json()
    except Exception:
      return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content={"error": "SERVICE UNAVAILABLE"})
  else:
    return await vrouter.run('/' + path, request.method, ((await request.json()) if request.method != 'GET' else None))

app.mount("/", StaticFiles(directory="static", html=True), name="static")

@app.exception_handler(404)
async def not_found_handler(a, b):
  return FileResponse("static/index.html", status_code=200)



def serve():
  import uvicorn
  [protocol, slash2_host, port] = config.sys_webui_host.split(':')
  uvicorn.run(app, host=slash2_host[2:], port=int(port))

if __name__ == '__main__':
  serve()