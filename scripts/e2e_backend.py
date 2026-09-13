import sys
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE_URL = "http://127.0.0.1:3000/api"

def get(url):
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=5) as res:
        return res.status, json.loads(res.read().decode())

def post(url, data):
    body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=5) as res:
        return res.status, json.loads(res.read().decode())

def main():
    print("Running E2E verification against API...")
    try:
        status, h = get(f"{BASE_URL}/health")
        assert status == 200 and h.get("ok") is True, f"Health check failed: {status}"
        print("✓ Health check passed")

        status, exercises = get(f"{BASE_URL}/exercises")
        assert status == 200, f"Exercises endpoint failed: {status}"
        assert len(exercises) >= 30, "Exercise count < 30"
        print(f"✓ Exercises endpoint returned {len(exercises)} exercises")

        status, qa_data = get(f"{BASE_URL}/qa/pushups")
        assert status == 200, f"QA pushups failed: {status}"
        assert qa_data["passed"] is True, "QA pushups assertion failed"
        print("✓ QA pushups passed")

        status, sim_data = post(f"{BASE_URL}/simulate/timeline", {
            "age": 35,
            "sex": "male",
            "experience": "intermediate",
            "maxPushups": 25,
            "workout": [{"exercise_id": "pushup", "sets": 5, "reps": 20, "days_per_week": 7, "rir": 2}]
        })
        assert status == 200, f"Simulation failed: {status}"
        checkpoints = sim_data["checkpoints"]
        assert len(checkpoints) == 8, f"Expected 8 checkpoints, got {len(checkpoints)}"
        print(f"✓ Timeline simulation passed with {len(checkpoints)} checkpoints")

        print("\nALL E2E API VERIFICATIONS PASSED SUCCESSFULLY.")
    except Exception as e:
        print(f"E2E test error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
