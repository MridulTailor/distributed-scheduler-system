import urllib.request
import urllib.error
import json
import concurrent.futures
import time

GATEWAY_URL = "http://localhost:8000/sessions"

def make_request():
    req = urllib.request.Request(GATEWAY_URL, method="POST")
    try:
        with urllib.request.urlopen(req) as response:
            return response.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception as e:
        return 500

def test_high_load():
    print("--- Testing High Load Concurrency ---")
    print("Sending 200 concurrent requests to the Gateway (NGINX Load Balancer)...")
    
    success_count = 0
    rejected_count = 0
    error_count = 0
    
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(make_request) for _ in range(200)]
        for future in concurrent.futures.as_completed(futures):
            status = future.result()
            if status == 200:
                success_count += 1
            elif status == 503:
                rejected_count += 1
            else:
                error_count += 1
                
    end_time = time.time()
    
    print(f"Time taken: {end_time - start_time:.2f} seconds")
    print(f"Total successful allocations: {success_count} (Expected <= 30)")
    print(f"Total rejected allocations (503): {rejected_count} (Expected >= 170)")
    print(f"Total errors: {error_count} (Expected 0)")
    
    if success_count <= 30 and error_count == 0:
        print("✅ High load concurrency test passed! The system remained stable under load.")
    else:
        print("❌ High load concurrency test failed!")

if __name__ == "__main__":
    test_high_load()
