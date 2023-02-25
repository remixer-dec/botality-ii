from contextlib import contextmanager
from collections import defaultdict

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
            yield True
            self.task_count[user_id] -= 1
        else:
            yield False
            
