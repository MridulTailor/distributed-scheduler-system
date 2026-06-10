from fastapi import FastAPI, HTTPException
import logging
from datetime import datetime
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = FastAPI()

import redis.asyncio as redis
from config import REDIS_URL, INITIAL_NODES
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
        raise HTTPException(status_code=404, detail="Node not found")
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
        raise HTTPException(status_code=404, detail="Node not found")
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
        raise HTTPException(status_code=404, detail="Node not found")
    elif result == -1:
        return {"success": False, "reason": "node_unhealthy"}
    elif result == -2:
        return {"success": False, "reason": "capacity_exceeded"}
        
    node = await redis_client.hgetall(f"node:{node_id}")
    node["capacity"] = int(node["capacity"])
    node["used"] = int(node["used"])
    node["healthy"] = node["healthy"] == "true"
    return {"success": True, "node": node}

@app.post("/nodes/{node_id}/release")
async def release_node(node_id: str):
    node = await redis_client.hgetall(f"node:{node_id}")
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
        
    used = int(node["used"])
    if used > 0:
        new_used = await redis_client.hincrby(f"node:{node_id}", "used", -1)
        node["used"] = new_used
    else:
        node["used"] = 0
        
    node["capacity"] = int(node["capacity"])
    node["healthy"] = node["healthy"] == "true"
    return node

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)