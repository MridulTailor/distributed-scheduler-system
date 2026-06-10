import urllib.request
import urllib.error
import json
import time

GATEWAY_URL = "http://localhost:8000/sessions"
NODE_MANAGER_URL = "http://localhost:8002/nodes"

def get_nodes():
    req = urllib.request.Request(NODE_MANAGER_URL, method="GET")
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode())["nodes"]

def mark_node_down(node_id):
    req = urllib.request.Request(f"{NODE_MANAGER_URL}/{node_id}/down", method="POST")
    with urllib.request.urlopen(req) as response:
        return response.status == 200
        
def mark_node_up(node_id):
    req = urllib.request.Request(f"{NODE_MANAGER_URL}/{node_id}/up", method="POST")
    with urllib.request.urlopen(req) as response:
        return response.status == 200

def test_node_failure():
    print("--- Testing Node Failure Routing ---")
    
    # 1. Ensure all nodes are up
    mark_node_up("node-1")
    mark_node_up("node-2")
    mark_node_up("node-3")
    
    # 2. Mark node-1 as DOWN
    print("Marking node-1 as DOWN...")
    mark_node_down("node-1")
    
    # 3. Create 5 sessions, ensure none land on node-1
    print("Creating 5 sessions...")
    allocated_nodes = set()
    req = urllib.request.Request(GATEWAY_URL, method="POST")
    
    for _ in range(5):
        try:
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                allocated_nodes.add(data["nodeId"])
        except urllib.error.HTTPError as e:
            print(f"Failed to create session: {e.code}")
            
    print(f"Sessions allocated to nodes: {allocated_nodes}")
    
    if "node-1" not in allocated_nodes:
        print("✅ Node failure test passed! No sessions were routed to the downed node.")
    else:
        print("❌ Node failure test failed! Sessions were routed to a downed node.")
        
    # Clean up
    print("Restoring node-1...")
    mark_node_up("node-1")

if __name__ == "__main__":
    test_node_failure()
