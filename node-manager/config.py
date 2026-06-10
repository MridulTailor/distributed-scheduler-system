import os

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")

INITIAL_NODES = [
    {"id": "node-1", "capacity": 10, "used": 0, "healthy": "true"},
    {"id": "node-2", "capacity": 10, "used": 0, "healthy": "true"},
    {"id": "node-3", "capacity": 10, "used": 0, "healthy": "true"},
]
