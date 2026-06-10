import urllib.request
import urllib.error
import json
import threading
import time

GATEWAY_URL = "http://localhost:8000/sessions"
NODE_MANAGER_URL = "http://localhost:8002/nodes"

def mark_node(node_id, action):
    req = urllib.request.Request(f"{NODE_MANAGER_URL}/{node_id}/{action}", method="POST")
    try:
        with urllib.request.urlopen(req) as response:
            pass
    except:
        pass

flapping = True

def flapper():
    while flapping:
        mark_node("node-1", "down")
        time.sleep(0.1)
        mark_node("node-1", "up")
        time.sleep(0.1)

def test_flapping_nodes():
    global flapping
    print("--- Testing Flapping Nodes ---")
    
    print("1. Starting background thread to flap node-1 UP and DOWN every 100ms...")
    t = threading.Thread(target=flapper)
    t.start()
    
    print("2. Attempting to create 20 sessions during flapping...")
    successes = 0
    failures = 0
    
    for i in range(20):
        req = urllib.request.Request(GATEWAY_URL, method="POST")
        try:
            with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    successes += 1
        except urllib.error.HTTPError:
            failures += 1
        time.sleep(0.05)
        
    print(f"Total successful allocations: {successes}")
    print(f"Total failed allocations: {failures}")
    
    flapping = False
    t.join()
    
    mark_node("node-1", "up") # Restore
    
    if successes == 20:
        print("✅ Flapping nodes test passed! The system gracefully handled the flapping node (routing around it or waiting for it).")
    else:
        print("❌ Flapping nodes test failed! Some sessions could not be allocated.")

if __name__ == "__main__":
    test_flapping_nodes()
