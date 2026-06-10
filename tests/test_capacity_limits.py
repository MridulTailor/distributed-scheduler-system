import urllib.request
import urllib.error
import json
import time

GATEWAY_URL = "http://localhost:8000/sessions"

def test_capacity_limits():
    print("--- Testing Capacity Limits ---")
    print("Attempting to allocate 35 sessions (Cluster max is 30).")
    
    success_count = 0
    failure_count = 0
    
    req = urllib.request.Request(GATEWAY_URL, method="POST")
    
    for i in range(35):
        try:
            with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    success_count += 1
        except urllib.error.HTTPError as e:
            if e.code == 503:
                failure_count += 1
            else:
                print(f"Unexpected HTTP error on request {i}: {e.code}")
        except Exception as e:
            print(f"Unexpected error on request {i}: {e}")
            
    print(f"Total successful allocations: {success_count} (Expected: 30)")
    print(f"Total rejected allocations: {failure_count} (Expected: 5)")
    
    if success_count == 30 and failure_count == 5:
        print("✅ Capacity limit test passed!")
    else:
        print("❌ Capacity limit test failed!")

if __name__ == "__main__":
    test_capacity_limits()
