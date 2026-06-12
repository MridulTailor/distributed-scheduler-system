import os
from enum import Enum

class RejectionReason(str, Enum):
    NODE_MANAGER_ERROR = "node_manager_error"
    NO_CAPACITY = "no_capacity"
    NODE_UNHEALTHY = "node_unhealthy"
    CAPACITY_EXCEEDED = "capacity_exceeded"

class ErrorDetail(str, Enum):
    COMMUNICATION_FAILED = "Failed to communicate with Node Manager"
    NO_CAPACITY = "No available capacity in the cluster"
    SESSION_NOT_FOUND = "Session not found"

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
NODE_MANAGER_URL = os.getenv("NODE_MANAGER_URL", "http://node-manager:8002")
POSTGRES_URL = os.getenv("POSTGRES_URL", "postgresql://scheduler_user:scheduler_password@postgres:5432/scheduler_db")
