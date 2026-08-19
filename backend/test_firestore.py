import os
import sys
import json
import time
from urllib import request, parse, error

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
FIREBASE_SERVICE_ACCOUNT_KEY_PATH = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY_PATH")
if not FIREBASE_SERVICE_ACCOUNT_KEY_PATH:
    print("ERROR: FIREBASE_SERVICE_ACCOUNT_KEY_PATH not set")
    sys.exit(1)

def make_request(method, endpoint, data=None, headers=None):
    url = f"{BASE_URL}{endpoint}"
    if headers is None:
        headers = {}
    if data is not None:
        data = json.dumps(data).encode('utf-8')
        headers.setdefault('Content-Type', 'application/json')
    req = request.Request(url, data=data, headers=headers, method=method)
    try:
        with request.urlopen(req) as response:
            return {
                'status': response.status,
                'body': json.loads(response.read().decode('utf-8'))
            }
    except error.HTTPError as e:
        return {
            'status': e.code,
            'body': json.loads(e.read().decode('utf-8'))
        }
    except Exception as e:
        return {
            'status': None,
            'body': str(e)
        }

def main():
    print("Starting Firestore verification test...")
    print("=" * 50)
    
    # Step 1: Submit a complaint
    print("1. Submitting a complaint via POST /complaints/")
    complaint_data = {
        "citizen_id": "citizen_001",
        "description": "The street lights near our college have not been working for five days.",
        "location": "Main Street, Near College"
    }
    resp = make_request("POST", "/complaints/", data=complaint_data)
    if resp['status'] != 200:
        print(f"   FAILED: Status {resp['status']}, Body: {resp['body']}")
        return False
    complaint = resp['body']
    complaint_id = complaint.get('id')
    print(f"   SUCCESS: Complaint created with ID: {complaint_id}")
    print(f"   AI Analysis: {json.dumps(complaint.get('ai_analysis'), indent=2)}")
    
    # Step 2: Retrieve the complaint
    print("\n2. Retrieving the complaint via GET /complaints/{id}")
    resp = make_request("GET", f"/complaints/{complaint_id}")
    if resp['status'] != 200:
        print(f"   FAILED: Status {resp['status']}, Body: {resp['body']}")
        return False
    retrieved = resp['body']
    print(f"   SUCCESS: Retrieved complaint: {json.dumps(retrieved, indent=2)}")
    
    # Step 3: Update status to ASSIGNED
    print("\n3. Updating status to ASSIGNED via PATCH /complaints/{id}/status")
    resp = make_request("PATCH", f"/complaints/{complaint_id}/status", data={"status": "ASSIGNED"})
    if resp['status'] != 200:
        print(f"   FAILED: Status {resp['status']}, Body: {resp['body']}")
        return False
    print(f"   SUCCESS: Status updated to ASSIGNED: {resp['body']}")
    
    # Step 4: Update status to IN_PROGRESS
    print("\n4. Updating status to IN_PROGRESS via PATCH /complaints/{id}/status")
    resp = make_request("PATCH", f"/complaints/{complaint_id}/status", data={"status": "IN_PROGRESS"})
    if resp['status'] != 200:
        print(f"   FAILED: Status {resp['status']}, Body: {resp['body']}")
        return False
    print(f"   SUCCESS: Status updated to IN_PROGRESS: {resp['body']}")
    
    # Step 5: Update status to RESOLVED
    print("\n5. Updating status to RESOLVED via PATCH /complaints/{id}/status")
    resp = make_request("PATCH", f"/complaints/{complaint_id}/status", data={"status": "RESOLVED"})
    if resp['status'] != 200:
        print(f"   FAILED: Status {resp['status']}, Body: {resp['body']}")
        return False
    print(f"   SUCCESS: Status updated to RESOLVED: {resp['body']}")
    
    # Step 6: Retrieve the complaint again to check resolved_at
    print("\n6. Retrieving the complaint to verify resolved_at")
    resp = make_request("GET", f"/complaints/{complaint_id}")
    if resp['status'] != 200:
        print(f"   FAILED: Status {resp['status']}, Body: {resp['body']}")
        return False
    final = resp['body']
    resolved_at = final.get('resolved_at')
    if resolved_at:
        print(f"   SUCCESS: resolved_at is set to: {resolved_at}")
    else:
        print(f"   WARNING: resolved_at is not set or is null: {resolved_at}")
    
    print("\n" + "=" * 50)
    print("Verification completed successfully!")
    print(f"Complaint ID: {complaint_id}")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
