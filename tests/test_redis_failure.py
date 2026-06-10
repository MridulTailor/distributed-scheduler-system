import subprocess
import urllib.request
import urllib.error
import time

GATEWAY_URL = "http://localhost:8000/sessions"

def run_cmd(cmd):
    subprocess.run(cmd, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def make_request():
    req = urllib.request.Request(GATEWAY_URL, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            return response.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception as e:
        return 500

def test_redis_failure():
    print("--- Testing Redis Failure / Recovery ---")
    
    print("1. Testing normal allocation...")
    status = make_request()
    if status == 200:
        print("   ✅ Allocation succeeded")
    else:
        print(f"   ❌ Allocation failed with status {status}")
        
    print("2. Pausing Redis container (Simulating failure)...")
    run_cmd("docker compose pause redis")
    time.sleep(2)
    
    print("3. Testing allocation during failure...")
    status = make_request()
    if status == 500:
        print("   ✅ System correctly failed (500 Internal Error) as Redis is down.")
    else:
        print(f"   ❌ Expected 500, got {status}")
        
    print("4. Unpausing Redis container (Simulating recovery)...")
    run_cmd("docker compose unpause redis")
    time.sleep(2)
    
    print("5. Testing allocation after recovery...")
    status = make_request()
    if status == 200:
        print("   ✅ System successfully recovered and allocation succeeded.")
    else:
        print(f"   ❌ System failed to recover. Got status {status}")

if __name__ == "__main__":
    test_redis_failure()
