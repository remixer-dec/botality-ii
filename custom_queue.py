from contextlib import contextmanager
from collections import defaultdict
import time

class UserLimitedQueue:
  max_tasks_per_user = None

  def __init__(self, max_tasks_per_user):
    self.task_count = defaultdict(int)
    if self.max_tasks_per_user is None:
      self.max_tasks_per_user = max_tasks_per_user

  @contextmanager
  def for_user(self, user_id):
    if self.task_count[user_id] < self.max_tasks_per_user:
      self.task_count[user_id] += 1
      try:
        yield True
      finally:
        self.task_count[user_id] -= 1
    else:
      yield False
      
class CallCooldown:
  calls = {}

  @classmethod
  def check_call(cls, uid, function_name, timeout=30):
    key = f'{uid}_{function_name}'
    if key in cls.calls:
      if time.time() - cls.calls[key] < timeout:
        return False
    cls.calls[key] = time.time()
    return True

def semaphore_wrapper(semaphore, callback):
  async def wrapped(*args, **kwargs):
    async with semaphore:
      return await callback(*args, **kwargs)
  return wrapped
    