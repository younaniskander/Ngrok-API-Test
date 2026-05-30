import requests
import json
import random

BASE_URL = "http://127.0.0.1:8000"
RESULTS_FILE = "api_test_results.json"

def run_tests():
    results = {}
    
    print(f"Testing endpoints at {BASE_URL}...")
    
    # Test 1: Health Check
    try:
        health_res = requests.get(f"{BASE_URL}/health")
        results["/health"] = {
            "status_code": health_res.status_code,
            "response": health_res.json()
        }
        print("GET /health - OK")
    except Exception as e:
        results["/health"] = {"error": str(e)}
        print(f"GET /health - FAILED: {e}")

    # Test 2: Prediction Endpoint
    try:
        # Generate dummy EMG data: 200 samples x 4 channels
        dummy_window = [[random.uniform(-0.1, 0.1) for _ in range(4)] for _ in range(200)]
        
        predict_res = requests.post(
            f"{BASE_URL}/predict",
            json={"emg_window": dummy_window}
        )
        
        results["/predict"] = {
            "status_code": predict_res.status_code,
            "response": predict_res.json()
        }
        print("POST /predict - OK")
    except Exception as e:
        results["/predict"] = {"error": str(e)}
        print(f"POST /predict - FAILED: {e}")

    # Save to file
    with open(RESULTS_FILE, 'w') as f:
        json.dump(results, f, indent=4)
        
    print(f"\nAll tests completed! Results saved to {RESULTS_FILE}")

if __name__ == "__main__":
    run_tests()
