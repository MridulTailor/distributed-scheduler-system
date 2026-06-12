import urllib.request
import urllib.error
import time

def simulate_load():
    url = "http://localhost:8000/sessions"
    print("Starting load test...")
    success_count = 0
    reject_count = 0
    
    for i in range(50):
        req = urllib.request.Request(url, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=5.0) as response:
                if response.status == 200:
                    success_count += 1
                    print(f"[{i+1}/50] 🟢 Allocated session successfully")
        except urllib.error.HTTPError as e:
            reject_count += 1
            print(f"[{i+1}/50] 🔴 Rejected: HTTP {e.code}")
        except Exception as e:
            print(f"[{i+1}/50] ❌ Error: {e}")
            
        time.sleep(0.05)
        
    print("\n--- Load Test Complete ---")
    print(f"Successfully Allocated: {success_count}")
    print(f"Rejected: {reject_count}")
    print("Check Grafana now! Your metrics should be populated.")

if __name__ == "__main__":
    simulate_load()
