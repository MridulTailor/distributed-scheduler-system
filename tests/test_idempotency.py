import urllib.request
import urllib.error
import json

GATEWAY_URL = "http://localhost:8000/sessions"

def make_delete_request(session_id):
    req = urllib.request.Request(f"{GATEWAY_URL}/{session_id}", method="DELETE")
    try:
        with urllib.request.urlopen(req) as response:
            return response.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception as e:
        return 500

def test_idempotency():
    print("--- Testing Idempotency (Session Deletion) ---")
    
    # Create a session
    req = urllib.request.Request(GATEWAY_URL, method="POST")
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            session_id = data["id"]
            print(f"1. Created session {session_id}")
    except Exception as e:
        print(f"Failed to create session: {e}")
        return
        
    # First delete
    status1 = make_delete_request(session_id)
    print(f"2. First delete request returned status {status1}")
    
    # Second delete (should be idempotent/safe, return 404 since it doesn't exist)
    status2 = make_delete_request(session_id)
    print(f"3. Second delete request returned status {status2}")
    
    if status1 == 200 and status2 == 404:
        print("✅ Idempotency test passed! Repeated deletes do not crash the system.")
    else:
        print("❌ Idempotency test failed!")

if __name__ == "__main__":
    test_idempotency()
