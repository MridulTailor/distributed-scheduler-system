import urllib.request
import urllib.error
import json

GATEWAY_URL = "http://localhost:8000/sessions"
NODE_MANAGER_URL = "http://localhost:8002/nodes"

def get_total_used():
    req = urllib.request.Request(NODE_MANAGER_URL, method="GET")
    with urllib.request.urlopen(req) as response:
        nodes = json.loads(response.read().decode())["nodes"]
        return sum(node["used"] for node in nodes)

def test_capacity_leak():
    print("--- Testing Capacity Leak ---")
    
    initial_used = get_total_used()
    print(f"1. Initial total used capacity: {initial_used}")
    
    print("2. Creating and deleting 15 sessions iteratively...")
    for _ in range(15):
        # Create
        req = urllib.request.Request(GATEWAY_URL, method="POST")
        with urllib.request.urlopen(req) as response:
            session_id = json.loads(response.read().decode())["id"]
            
        # Delete
        req_del = urllib.request.Request(f"{GATEWAY_URL}/{session_id}", method="DELETE")
        with urllib.request.urlopen(req_del) as response:
            pass

    final_used = get_total_used()
    print(f"3. Final total used capacity: {final_used}")
    
    if initial_used == final_used:
        print("✅ Capacity leak test passed! No capacity was leaked during create/delete cycles.")
    else:
        print("❌ Capacity leak test failed! Capacity was not properly restored.")

if __name__ == "__main__":
    test_capacity_leak()
