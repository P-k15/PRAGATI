import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

def post_complaint(description, location, citizen_id="citizen_test"):
    payload = {
        "description": description,
        "location": location,
        "citizen_id": citizen_id
    }
    response = requests.post(f"{BASE_URL}/complaints/", json=payload)
    return response.json(), response.status_code

def get_complaint(complaint_id):
    response = requests.get(f"{BASE_URL}/complaints/{complaint_id}")
    return response.json(), response.status_code

def run_sla_check():
    response = requests.post(f"{BASE_URL}/complaints/check-sla")
    return response.json(), response.status_code

def main():
    print("=== Phase 5.3 Test ===")

    # Test complaints
    test_cases = [
        ("The street lights near our college have not been working for five days.", "Near ABC College, Street 5"),
        ("Garbage has not been collected from our area for three days and it is creating a bad smell.", "XYZ Colony, Main Road"),
        ("A major water pipeline has burst and water is flooding the road.", "Main Highway, Near Bridge"),
        ("There is a large pothole on the main road causing accidents.", "City Center, Main Street")
    ]

    complaint_ids = []

    for desc, loc in test_cases:
        print(f"\nSubmitting complaint: {desc[:50]}...")
        result, status = post_complaint(desc, loc)
        if status == 200:
            complaint_id = result.get("id")
            complaint_ids.append(complaint_id)
            print(f"  Created complaint ID: {complaint_id}")
            print(f"  Status: {result.get('status')}")
            print(f"  Department: {result.get('department')}")
            print(f"  Assigned Officer: {result.get('assigned_officer')}")
            print(f"  Routing Source: {result.get('routing_source')}")
            print(f"  SLA Status: {result.get('sla_status')}")
            print(f"  Escalated: {result.get('escalated')}")
        else:
            print(f"  Failed: {result}")

    # Wait a bit for any background processes (none, but just in case)
    time.sleep(2)

    # Run SLA check
    print("\n--- Running SLA check ---")
    sla_result, sla_status = run_sla_check()
    if sla_status == 200:
        print(f"SLA Check Results: {json.dumps(sla_result, indent=2)}")
    else:
        print(f"SLA check failed: {sla_result}")

    # Check each complaint after SLA check
    print("\n--- Complaint status after SLA check ---")
    for cid in complaint_ids:
        comp, status = get_complaint(cid)
        if status == 200:
            print(f"ID {cid}:")
            print(f"  Status: {comp.get('status')}")
            print(f"  SLA Status: {comp.get('sla_status')}")
            print(f"  Escalated: {comp.get('escalated')}")
            print(f"  Escalation Level: {comp.get('escalation_level')}")
            print(f"  Assigned Officer: {comp.get('assigned_officer')}")
        else:
            print(f"Failed to get complaint {cid}: {comp}")

    # Test manual assignment still works
    if complaint_ids:
        test_cid = complaint_ids[0]
        print(f"\n--- Testing manual assignment on {test_cid} ---")
        # First, maybe change status to AI_PROCESSED if it's ASSIGNED? We'll just assign to a different officer.
        # Let's pick officer_001 (Electrical Maintenance) and assign manually.
        payload = {"officer_id": "officer_001"}
        response = requests.patch(f"{BASE_URL}/complaints/{test_cid}/assign", json=payload)
        if response.status_code == 200:
            result = response.json()
            print(f"Manual assignment successful:")
            print(f"  Status: {result.get('status')}")
            print(f"  Assigned Officer: {result.get('assigned_officer')}")
            print(f"  Routing Source: {result.get('routing_source')}")
        else:
            print(f"Manual assignment failed: {response.json()}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error during test: {e}")