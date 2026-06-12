from fastapi import FastAPI, HTTPException, Response
import logging
from datetime import datetime
from pydantic import BaseModel
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from metrics import NODE_UTILIZATION, HEALTHY_NODES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = FastAPI()

import redis.asyncio as redis
from config import REDIS_URL, INITIAL_NODES, RejectionReason, ErrorDetail
from scripts import ALLOCATE_LUA

redis_client = redis.from_url(REDIS_URL, decode_responses=True)

@app.on_event("startup")
async def startup_event():
    # Only initialize if they don't exist
    for node in INITIAL_NODES:
        exists = await redis_client.exists(f"node:{node['id']}")
        if not exists:
            await redis_client.hset(f"node:{node['id']}", mapping=node)

@app.get("/nodes")
async def get_nodes():
    keys = await redis_client.keys("node:*")
    nodes = []
    for key in keys:
        node = await redis_client.hgetall(key)
        # Parse integers and booleans
        node["capacity"] = int(node["capacity"])
        node["used"] = int(node["used"])
        node["healthy"] = node["healthy"] == "true"
        nodes.append(node)
    # Sort nodes by id for deterministic output
    nodes.sort(key=lambda x: x["id"])
    return {"nodes": nodes}

@app.post("/nodes/{node_id}/down")
async def mark_node_down(node_id: str):
    exists = await redis_client.exists(f"node:{node_id}")
    if not exists:
        raise HTTPException(status_code=404, detail=ErrorDetail.NODE_NOT_FOUND)
    await redis_client.hset(f"node:{node_id}", "healthy", "false")
    node = await redis_client.hgetall(f"node:{node_id}")
    node["capacity"] = int(node["capacity"])
    node["used"] = int(node["used"])
    node["healthy"] = False
    return node

@app.post("/nodes/{node_id}/up")
async def mark_node_up(node_id: str):
    exists = await redis_client.exists(f"node:{node_id}")
    if not exists:
        raise HTTPException(status_code=404, detail=ErrorDetail.NODE_NOT_FOUND)
    await redis_client.hset(f"node:{node_id}", "healthy", "true")
    node = await redis_client.hgetall(f"node:{node_id}")
    node["capacity"] = int(node["capacity"])
    node["used"] = int(node["used"])
    node["healthy"] = True
    return node

@app.post("/nodes/{node_id}/allocate")
async def allocate_node(node_id: str):
    try:
        result = await redis_client.eval(ALLOCATE_LUA, 1, f"node:{node_id}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    if result == -3:
        raise HTTPException(status_code=404, detail=ErrorDetail.NODE_NOT_FOUND)
    elif result == -1:
        return {"success": False, "reason": RejectionReason.NODE_UNHEALTHY}
    elif result == -2:
        return {"success": False, "reason": RejectionReason.CAPACITY_EXCEEDED}
        
    node = await redis_client.hgetall(f"node:{node_id}")
    node["capacity"] = int(node["capacity"])
    node["used"] = int(node["used"])
    node["healthy"] = node["healthy"] == "true"
    return {"success": True, "node": node}

@app.post("/nodes/{node_id}/release")
async def release_node(node_id: str):
    node = await redis_client.hgetall(f"node:{node_id}")
    if not node:
        raise HTTPException(status_code=404, detail=ErrorDetail.NODE_NOT_FOUND)
        
    used = int(node["used"])
    if used > 0:
        new_used = await redis_client.hincrby(f"node:{node_id}", "used", -1)
        node["used"] = new_used
    else:
        node["used"] = 0
        
    node["capacity"] = int(node["capacity"])
    node["healthy"] = node["healthy"] == "true"
    return node

@app.get("/metrics")
async def metrics():
    keys = await redis_client.keys("node:*")
    healthy_count = 0
    for key in keys:
        node = await redis_client.hgetall(key)
        node_id = node.get("id")
        if not node_id:
            continue
            
        capacity = int(node.get("capacity", 0))
        used = int(node.get("used", 0))
        is_healthy = node.get("healthy") == "true"
        
        utilization = (used / capacity * 100) if capacity > 0 else 0.0
        # Assuming single resource type for simplicity based on your current setup
        NODE_UTILIZATION.labels(node_id=node_id, resource_type='compute').set(utilization)
        
        if is_healthy:
            healthy_count += 1
            
    HEALTHY_NODES.set(healthy_count)
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)