import torch
import sys
import psutil
from config_reader import config
from time import time 
import logging

logger = logging.getLogger(__name__)

process = psutil.Process()
SHARED_MEMORY = sys.platform == "darwin"
GPU_AVAILABLE = torch.cuda.is_available()


def get_vram_info():
  if torch.cuda.is_available():
    device = torch.cuda.current_device()
    vram_bytes = torch.cuda.get_device_properties(device).total_memory
    try:
      vram_bytes, total = torch.cuda.mem_get_info()
    except Exception:
      pass
    free_gb = vram_bytes / (1024**3)
    total_gb = total / (1024**3)
    return free_gb, total_gb
  else:
    return 0.0, 0.0

def get_system_ram_info():
  virtual_memory = psutil.virtual_memory()
  free_gb = virtual_memory.available / (1024**3)
  total_gb = virtual_memory.total / (1024**3)
  return free_gb, total_gb

class MModel:
  def __init__(self, name, load, unload):
    self.name = name
    self.model = load()
    self.load = load
    self.unload = unload
    self.memory = 0
  def __setattr__(self, name, value):
    self.__dict__[name] = value

class MemoryManager:
  def __init__(self, get_memory, cached_model_count):
    self.get_memory = get_memory
    self.starting_memory, self.total_memory = get_memory()
    self.cache = {}
    self.cached_model_count = cached_model_count
    self.mm_management_policy = config.mm_management_policy
  
  def wrap(self, model_name, load_function=None, unload_function=None, memory='auto'):
    mem, total_mem = self.get_memory()
    # get keys and values of items with model != None as lists
    [*alive_keys], [*alive_values] = zip(*((i.name, i) for i in self.cache.values() if i.model is not None)) \
      if len(self.cache.keys()) > 0 else ([],[])
    if config.mm_autounload_after_seconds > 0:
      seconds = config.mm_autounload_after_seconds
      for key in alive_keys:
        if key != model_name and self.cache[key].last_used + seconds < time():
          self.unload(key, 'timeout')
          alive_keys.remove(key)
          alive_values.remove(self.cache[key])
    if model_name not in self.cache:
      self.cache[model_name] = MModel(model_name, load_function, unload_function)
      self.cache[model_name].last_loaded = time()
    elif not self.cache[model_name].model:
      self.cache[model_name].model = load_function()
      self.cache[model_name].last_loaded = time()
    mem_diff = mem - self.get_memory()[0]
    mem_diff = mem_diff * int(mem_diff > 0)
    item = self.cache[model_name]
    item.memory = (mem_diff if memory == 'auto' else memory(item.model) or mem_diff)
    item.last_used = time()
    item.use_count = (item.use_count + 1) if hasattr(item, 'use_count') else 1
    if self.mm_management_policy == 'COUNT' or self.mm_management_policy == 'BOTH':
      cache_count = len(alive_keys)
      if cache_count > 0 and cache_count > self.cached_model_count:
        unloaded_key = self.unload_by_policy(model_name, alive_values, f'management policy {self.mm_management_policy}')
        if self.mm_management_policy == 'BOTH':
          alive_keys.remove(unloaded_key)
          alive_values.remove(self.cache[unloaded_key])
    if (self.mm_management_policy == 'MEMORY' or self.mm_management_policy == 'BOTH') \
    and (len(alive_values) > 0):
      items_memory = list(item.memory for item in alive_values)
      total_memory_used = sum(items_memory)
      memory_available, memory_total = self.get_memory()
      # TODO: find optimal value for mm_unload_memory_ratio on low-end devices and make it configurable
      mm_unload_memory_ratio = 3
      # if memory_available < max(items_memory) * 1.3 \
      if memory_available < self.starting_memory/mm_unload_memory_ratio \
      or total_memory_used * (1+1/mm_unload_memory_ratio) > self.starting_memory:
        self.unload_by_policy(model_name, alive_values, f'management policy {self.mm_management_policy}')
    return self.cache[model_name].model

  def unload(self, name, reason):
    target = self.cache[name]
    if target.unload is not None:
      target.unload(target.model)
    self.cache[name].model = None
    logger.info('removed', name, 'from model cache by memory manager due to', reason)

  def unload_by_policy(self, model_name, items, reason):
    if config.mm_unload_order_policy == 'LEAST_USED':
      items = sorted(items, key=lambda x: x.use_count)
    if config.mm_unload_order_policy == 'OLDEST_USE_TIME':
      items = sorted(items, key=lambda x: x.last_used)
    if config.mm_unload_order_policy == 'OLDEST_LOAD_ORDER':
      items = sorted(items, key=lambda x: x.last_loaded)
    if config.mm_unload_order_policy == 'MEMORY_FOOTPRINT':
      items = sorted(items, key=lambda x: x.memory)[::-1]
    to_unload = items[0].name
    if to_unload == model_name and len(items) > 1:
      to_unload = items[1].name
    self.unload(to_unload, config.mm_unload_order_policy, reason)
    return to_unload

  def stats(self):
    return {
      "starting_memory": round(self.starting_memory, 3),
      "total_memory": self.total_memory,
      "current_memory": round(self.get_memory()[0], 3),
      "cache": [{self.cache[key].name: round(self.cache[key].memory, 3)} for key in self.cache],
      "process": round(process.memory_info().rss / 1024**3, 2) if self == RAM else None
    }
    
RAM = MemoryManager(get_system_ram_info, config.mm_ram_cached_model_count_limit)
VRAM = MemoryManager(get_vram_info, config.mm_vram_cached_model_count_limit) if GPU_AVAILABLE else False

def mload(*args, gpu=False, **kwargs):
  if 'gpu' in kwargs and kwargs['gpu'] and GPU_AVAILABLE:
    return VRAM.wrap(*args, **kwargs)
  else:
    return RAM.wrap(*args, **kwargs)