from fastapi.responses import JSONResponse
from typing import Dict, Any
from fastapi import status, Body
from config_reader import config, Settings

def add_common_endpoints(app):
  @app.patch("/config")
  async def write_config(data: Dict[str, Any]):
    for key in data:
      try:
        if (getattr(config, key, None)) is not None:
          setattr(config, key, data[key])
      except Exception as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={'error': str(e)})
    return {"response": "ok"}

  @app.get("/config")
  async def read_config():
    return config

  @app.get("/schema")
  async def schema():
    return Settings.model_json_schema()


class VirtualRouter:
  def __init__(self):
    self.routes = {}

  def add_route(self, path, method, handler):
    self.routes[(path, method)] = handler

  def get(self, path):
    def decorator(handler):
      self.add_route(path, "GET", handler)
      return handler
    return decorator

  def patch(self, path):
    def decorator(handler):
      self.add_route(path, "PATCH", handler)
      return handler
    return decorator

  def post(self, path):
    def decorator(handler):
      self.add_route(path, "POST", handler)
      return handler
    return decorator

  async def run(self, path, method, data=None):
    handler = self.routes.get((path, method))
    if handler:
      if data:
        return await handler(data)
      else:
        return await handler()
    else:
      return {"error": "Server not available"}