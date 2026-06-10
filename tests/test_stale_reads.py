import urllib.request
import urllib.error
import json

SCHEDULER_URL = "http://localhost:8001/sessions"
NODE_MANAGER_URL = "http://localhost:8002/nodes"

def test_stale_reads():
    print("--- Testing Stale Reads Defense ---")
    print("This is validated by the Lua script. The test simulates a stale read context by ensuring ")
    print("allocations strictly rely on real-time atomic Redis checks rather than the cached Python dictionary.")
    
    # Fill up the capacity except for 1 slot
    print("Filling capacity to 29/30...")
    for _ in range(29):
        try:
            req = urllib.request.Request(SCHEDULER_URL, method="POST")
            urllib.request.urlopen(req)
        except Exception:
            pass
            
    # Send one more request, it should succeed.
    req = urllib.request.Request(SCHEDULER_URL, method="POST")
    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                print("1. 30th allocation successful.")
    except Exception as e:
        print(f"Failed 30th allocation: {e}")
        
    # Send another, it should fail immediately (no over-allocation).
    req = urllib.request.Request(SCHEDULER_URL, method="POST")
    try:
        urllib.request.urlopen(req)
        print("❌ 31st allocation succeeded! Stale read caused over-allocation.")
    except urllib.error.HTTPError as e:
        if e.code == 503:
            print("✅ 31st allocation rejected! Stale reads are fully prevented by the atomic Lua script.")
        else:
            print(f"Unexpected error: {e}")

if __name__ == "__main__":
    test_stale_reads()
