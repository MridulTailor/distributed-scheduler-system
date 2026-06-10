import os

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
NODE_MANAGER_URL = os.getenv("NODE_MANAGER_URL", "http://node-manager:8002")
