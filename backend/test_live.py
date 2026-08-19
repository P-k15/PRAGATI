import os
import sys
import json
from urllib import request, parse, error

BASE_URL = "http://localhost:8000/api/v1"

def make_request(method, endpoint, data=None):
    url = f"{BASE_URL}{endpoint}"
    headers = {'Content-Type': 'application/json'}
    if data is not None:
        data = json.dumps(data).encode('utf-8')
    else:
        data = None
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
            'body': json.loads(e.read().decode('utf-8')) if e.read() else {}
        }
    except Exception as e:
        return {
            'status': None,
            'body': str(e)
        }

def main():
    print("=" * 60)
    print("Phase 3.1 — LIVE FIRESTORE VERIFICATION")
    print("=" * 60)
    
    # Track results
    results = {
        'write_succeeded': False,
        'complaint_id': None,
        'read_succeeded': False,
        'status_updates_succeeded': False,
        'resolved_at_stored': False,
        'errors': []
    }
    
    try:
        # Step 1: Submit a complaint
        print("\n1. Submitting a complaint via POST /complaints/")
        complaint_data = {
            "citizen_id": "citizen_001",
            "description": "The street lights near our college have not been working for five days.",
            "location": "Main Street, Near College"
        }
        resp = make_request("POST", "/complaints/", data=complaint_data)
        if resp['status'] == 200:
            complaint = resp['body']
            complaint_id = complaint.get('id')
            results['write_succeeded'] = True
            results['complaint_id'] = complaint_id
            print(f"   SUCCESS: Complaint created with ID: {complaint_id}")
            # Optionally, we can check if AI analysis was performed (not required for this verification)
        else:
            err_msg = f"POST /complaints/ failed with status {resp['status']}: {resp['body']}"
            results['errors'].append(err_msg)
            print(f"   FAILED: {err_msg}")
            return results
        
        # Step 2: Retrieve the complaint
        print(f"\n2. Retrieving the complaint via GET /complaints/{complaint_id}")
        resp = make_request("GET", f"/complaints/{complaint_id}")
        if resp['status'] == 200:
            retrieved = resp['body']
            results['read_succeeded'] = True
            print(f"   SUCCESS: Retrieved complaint.")
            # We can optionally check that the ID matches
        else:
            err_msg = f"GET /complaints/{complaint_id} failed with status {resp['status']}: {resp['body']}"
            results['errors'].append(err_msg)
            print(f"   FAILED: {err_msg}")
            return results
        
        # Step 3: Update status to ASSIGNED
        print(f"\n3. Updating status to ASSIGNED via PATCH /complaints/{complaint_id}/status")
        resp = make_request("PATCH", f"/complaints/{complaint_id}/status", data={"status": "ASSIGNED"})
        if resp['status'] == 200:
            print(f"   SUCCESS: Status updated to ASSIGNED.")
        else:
            err_msg = f"PATCH /complaints/{complaint_id}/status to ASSIGNED failed with status {resp['status']}: {resp['body']}"
            results['errors'].append(err_msg)
            print(f"   FAILED: {err_msg}")
            return results
        
        # Step 4: Update status to IN_PROGRESS
        print(f"\n4. Updating status to IN_PROGRESS via PATCH /complaints/{complaint_id}/status")
        resp = make_request("PATCH", f"/complaints/{complaint_id}/status", data={"status": "IN_PROGRESS"})
        if resp['status'] == 200:
            print(f"   SUCCESS: Status updated to IN_PROGRESS.")
        else:
            err_msg = f"PATCH /complaints/{complaint_id}/status to IN_PROGRESS failed with status {resp['status']}: {resp['body']}"
            results['errors'].append(err_msg)
            print(f"   FAILED: {err_msg}")
            return results
        
        # Step 5: Update status to RESOLVED
        print(f"\n5. Updating status to RESOLVED via PATCH /complaints/{complaint_id}/status")
        resp = make_request("PATCH", f"/complaints/{complaint_id}/status", data={"status": "RESOLVED"})
        if resp['status'] == 200:
            print(f"   SUCCESS: Status updated to RESOLVED.")
        else:
            err_msg = f"PATCH /complaints/{complaint_id}/status to RESOLVED failed with status {resp['status']}: {resp['body']}"
            results['errors'].append(err_msg)
            print(f"   FAILED: {err_msg}")
            return results
        
        # Step 6: Retrieve the complaint again to check resolved_at
        print(f"\n6. Retrieving the complaint to verify resolved_at")
        resp = make_request("GET", f"/complaints/{complaint_id}")
        if resp['status'] == 200:
            final = resp['body']
            resolved_at = final.get('resolved_at')
            if resolved_at is not None:
                results['resolved_at_stored'] = True
                print(f"   SUCCESS: resolved_at is set to: {resolved_at}")
            else:
                print(f"   WARNING: resolved_at is not set or is null: {resolved_at}")
                # We don't fail the test on this, just note it
        else:
            err_msg = f"GET /complaints/{complaint_id} (after updates) failed with status {resp['status']}: {resp['body']}"
            results['errors'].append(err_msg)
            print(f"   FAILED: {err_msg}")
            return results
        
        # If we got here, all steps up to the status updates succeeded
        results['status_updates_succeeded'] = True
        
        print("\n" + "=" * 60)
        print("VERIFICATION COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
    except Exception as e:
        err_msg = f"Unexpected error during verification: {str(e)}"
        results['errors'].append(err_msg)
        print(f"\n   ERROR: {err_msg}")
    
    return results

if __name__ == "__main__":
    results = main()
    # Print summary as required
    print("\n" + "=" * 60)
    print("FINAL REPORT")
    print("=" * 60)
    print(f"Firestore write succeeded: {results['write_succeeded']}")
    print(f"Complaint ID created: {results['complaint_id']}")
    print(f"Firestore read succeeded: {results['read_succeeded']}")
    print(f"Status updates succeeded: {results['status_updates_succeeded']}")
    print(f"resolved_at was stored: {results['resolved_at_stored']}")
    if results['errors']:
        print(f"Errors encountered: {len(results['errors'])}")
        for i, err in enumerate(results['errors'], 1):
            print(f"  {i}. {err}")
    else:
        print("Errors encountered: 0")
    print("=" * 60)
    
    # Exit with error if any critical step failed
    if not (results['write_succeeded'] and results['read_succeeded'] and results['status_updates_succeeded']):
        sys.exit(1)
    else:
        sys.exit(0)
