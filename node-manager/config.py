import os
from enum import Enum

class RejectionReason(str, Enum):
    NODE_UNHEALTHY = "node_unhealthy"
    CAPACITY_EXCEEDED = "capacity_exceeded"

class ErrorDetail(str, Enum):
    NODE_NOT_FOUND = "Node not found"

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")

INITIAL_NODES = [
    {"id": "node-1", "capacity": 10, "used": 0, "healthy": "true"},
    {"id": "node-2", "capacity": 10, "used": 0, "healthy": "true"},
    {"id": "node-3", "capacity": 10, "used": 0, "healthy": "true"},
]
