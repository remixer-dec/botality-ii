from fastapi.responses import JSONResponse
from typing import Dict, Any
from fastapi import status, Body
from config_reader import config, Settings
from asyncio import Lock, sleep
import os
import json

config_write_lock = Lock()

class DynamicConfig:
  def __init__(self, get_updated_config):
    self.get_updated_config = get_updated_config

  def __call__(self):
    if self.get_updated_config:
      return self.get_updated_config()
    else:
      return config

def add_common_endpoints(app, get_custom_config=False):
  get_config = DynamicConfig(get_custom_config)
  @app.patch("/config")
  async def write_config(data: Dict[str, Any]):
    for key in data:
      try:
        if (getattr(get_config(), key, None)) is not None:
          async with config_write_lock:
            setattr(get_config(), key, data[key])
      except Exception as e:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={'error': str(e)})
    return {"response": "ok"}

  @app.get("/config")
  async def read_config():
    return get_config()

  @app.get("/schema")
  async def schema():
    return Settings.model_json_schema() if hasattr(Settings, 'model_json_schema') else json.loads(Settings.schema_json())
  @app.get("/characters")
  async def characters():
    return {"response": [{'name': x[:-3], 'full': 'characters.' + x[:-3]} for x in os.listdir('characters/') \
      if not (x.startswith('.') or x.startswith('__'))]}


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