import asyncio
import os
import sys
import json
import time
from urllib import request, parse, error

BASE_URL = "http://127.0.0.1:8000/api/v1"

def make_http_request(method, endpoint, data=None):
    url = f"{BASE_URL}{endpoint}"
    headers = {'Content-Type': 'application/json'}
    encoded_data = json.dumps(data).encode('utf-8') if data is not None else None
    req = request.Request(url, data=encoded_data, headers=headers, method=method)
    try:
        with request.urlopen(req) as response:
            return {
                'status': response.status,
                'body': json.loads(response.read().decode('utf-8'))
            }
    except error.HTTPError as e:
        body_text = e.read().decode('utf-8') if e.fp else ""
        try:
            parsed_body = json.loads(body_text)
        except Exception:
            parsed_body = body_text
        return {'status': e.code, 'body': parsed_body}
    except Exception as e:
        return {'status': None, 'body': str(e)}

def run_master_test_suite():
    print("=" * 80)
    print("PRAGATI COMPREHENSIVE MASTER TEST SUITE")
    print("Testing every feature, endpoint, AI integration, routing, & state machine")
    print("=" * 80)

    test_results = []
    
    def log_test(test_name, success, details=""):
        status_str = "[PASS]" if success else "[FAIL]"
        print(f"{status_str} {test_name}")
        if details:
            print(f"       Details: {details}")
        test_results.append({'name': test_name, 'success': success, 'details': details})

    # 1. API Health Check
    print("\n--- SECTION 1: System & Auth Endpoints ---")
    resp = make_http_request("GET", "/health")
    # Note: /health is at root /health, let's try root as well if /api/v1/health is 404
    if resp['status'] != 200:
        req = request.Request("http://127.0.0.1:8000/health")
        try:
            with request.urlopen(req) as r:
                log_test("System Health Check", r.status == 200, "Backend API is online and healthy")
        except Exception as ex:
            log_test("System Health Check", False, str(ex))
    else:
        log_test("System Health Check", True, "API healthy")

    # 2. Citizen Registration
    reg_payload = {
        "email": f"test_citizen_{int(time.time())}@pragati.gov.in",
        "password": "SecurePassword123!",
        "full_name": "Rajesh Kumar",
        "role": "citizen"
    }
    reg_resp = make_http_request("POST", "/auth/register", reg_payload)
    log_test("Citizen Registration (/auth/register)", reg_resp['status'] in [200, 201], f"User ID: {reg_resp.get('body', {}).get('id')}")

    # 3. Citizen Login (Valid Credentials)
    login_payload = {
        "email": "citizen@example.com",
        "password": "citizenpass"
    }
    login_resp = make_http_request("POST", "/auth/login", login_payload)
    token_received = 'access_token' in login_resp.get('body', {})
    log_test("Citizen Login (/auth/login)", login_resp['status'] == 200 and token_received, f"Access Token received: {token_received}")

    # 4. Officer Login (Valid Credentials)
    off_login_payload = {
        "email": "officer@example.com",
        "password": "officerpass"
    }
    off_login_resp = make_http_request("POST", "/auth/login", off_login_payload)
    log_test("Officer Login (/auth/login)", off_login_resp['status'] == 200, "Officer JWT authenticated")

    # 5. Invalid Login Credentials Handling
    invalid_login_resp = make_http_request("POST", "/auth/login", {"email": "invalid@user.com", "password": "wrongpassword"})
    log_test("Invalid Credentials Rejection", invalid_login_resp['status'] in [401, 404, 422], f"Status code: {invalid_login_resp['status']}")

    # 6. Submit Complaint 1 (Electrical / Street Lighting - Nemotron AI Analysis)
    print("\n--- SECTION 2: AI Grievance Classification & Automated Routing ---")
    complaint_1_payload = {
        "citizen_id": "citizen_rajesh_01",
        "description": "Dangerous broken electric wire hanging near Sector 4 primary school posing live hazard.",
        "location": "Sector 4, Main School Road"
    }
    c1_resp = make_http_request("POST", "/complaints/", complaint_1_payload)
    c1_data = c1_resp.get('body', {})
    c1_id = c1_data.get('id')
    
    ai_success = bool(c1_data.get('category') and c1_data.get('summary') and c1_data.get('severity'))
    log_test(
        "Submit Grievance 1 (NVIDIA Nemotron AI Analysis)",
        c1_resp['status'] == 200 and ai_success,
        f"ID: {c1_id} | Category: {c1_data.get('category')} | Department: {c1_data.get('department')} | SLA: {c1_data.get('sla_hours')}h | AI Source: {c1_data.get('ai_source')}"
    )

    # 7. Verify Intelligent Workload-based Officer Assignment
    assigned_officer_1 = c1_data.get('assigned_officer')
    routing_ok = assigned_officer_1 is not None and c1_data.get('status') in ['ASSIGNED', 'AI_PROCESSED']
    log_test(
        "Automated Officer Routing Engine",
        routing_ok,
        f"Assigned Officer: {assigned_officer_1} | Status: {c1_data.get('status')} | Reason: {c1_data.get('routing_reason', 'N/A')}"
    )

    # 8. Submit Complaint 2 (Road Repair / Potholes)
    complaint_2_payload = {
        "citizen_id": "citizen_rajesh_01",
        "description": "Deep dangerous pothole on MG Road causing traffic congestion and accidents.",
        "location": "MG Road, Crossing 12"
    }
    c2_resp = make_http_request("POST", "/complaints/", complaint_2_payload)
    c2_data = c2_resp.get('body', {})
    c2_id = c2_data.get('id')
    log_test(
        "Submit Grievance 2 (Roads Department)",
        c2_resp['status'] == 200 and c2_id is not None,
        f"ID: {c2_id} | Category: {c2_data.get('category')} | Priority: {c2_data.get('priority')}"
    )

    # 9. Read Single Complaint Endpoint
    print("\n--- SECTION 3: Complaint Querying & Filtering ---")
    get_c1_resp = make_http_request("GET", f"/complaints/{c1_id}")
    get_c1_ok = get_c1_resp['status'] == 200 and get_c1_resp.get('body', {}).get('id') == c1_id
    log_test("Fetch Single Complaint (/complaints/{id})", get_c1_ok, f"Retrieved description: '{get_c1_resp.get('body', {}).get('description')[:40]}...'")

    # 10. List All Complaints
    list_resp = make_http_request("GET", "/complaints/")
    list_data = list_resp.get('body', [])
    list_ok = list_resp['status'] == 200 and isinstance(list_data, list) and len(list_data) > 0
    log_test("List Complaints (/complaints/)", list_ok, f"Total complaints retrieved: {len(list_data)}")

    # 11. Filter Complaints by Citizen ID
    filter_cit_resp = make_http_request("GET", "/complaints/?citizen_id=citizen_rajesh_01")
    filter_cit_data = filter_cit_resp.get('body', [])
    filter_cit_ok = filter_cit_resp['status'] == 200 and isinstance(filter_cit_data, list) and len(filter_cit_data) >= 2
    log_test("Filter Complaints by Citizen ID", filter_cit_ok, f"Matches found: {len(filter_cit_data)}")

    # 12. State Machine Lifecycle Transitions (IN_PROGRESS -> RESOLVED)
    print("\n--- SECTION 4: State Machine Lifecycle & Resolution ---")
    p_status_1 = make_http_request("PATCH", f"/complaints/{c1_id}/status", {"status": "IN_PROGRESS"})
    status_1_ok = p_status_1['status'] == 200 and p_status_1.get('body', {}).get('status') == 'IN_PROGRESS'
    log_test("Update Status to IN_PROGRESS", status_1_ok, f"New status: {p_status_1.get('body', {}).get('status')}")

    p_status_2 = make_http_request("PATCH", f"/complaints/{c1_id}/status", {"status": "RESOLVED"})
    res_data = p_status_2.get('body', {})
    resolved_ok = p_status_2['status'] == 200 and res_data.get('status') == 'RESOLVED' and res_data.get('resolved_at') is not None
    log_test(
        "Update Status to RESOLVED & Check resolved_at Timestamp",
        resolved_ok,
        f"Status: {res_data.get('status')} | resolved_at: {res_data.get('resolved_at')}"
    )

    # 13. Manual Officer Re-assignment Endpoint
    reassign_resp = make_http_request("PATCH", f"/complaints/{c2_id}/assign", {"officer_id": "officer_003"})
    reassign_ok = reassign_resp['status'] == 200 and reassign_resp.get('body', {}).get('assigned_officer') == "officer_003"
    log_test("Manual Officer Assignment (/complaints/{id}/assign)", reassign_ok, f"Assigned Officer: {reassign_resp.get('body', {}).get('assigned_officer')}")

    # 14. Invalid Status Update Error Handling
    invalid_status_resp = make_http_request("PATCH", f"/complaints/{c1_id}/status", {"status": "INVALID_STATE"})
    log_test("Reject Invalid State Transition", invalid_status_resp['status'] == 400, f"Error returned: {invalid_status_resp.get('body', {}).get('detail')}")

    # Final Report Summary
    print("\n" + "=" * 80)
    print("MASTER TEST SUITE FINAL REPORT")
    print("=" * 80)
    passed = sum(1 for r in test_results if r['success'])
    total = len(test_results)
    print(f"Total Tests Executed: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed / total) * 100:.1f}%")
    print("=" * 80)

    return total - passed == 0

if __name__ == "__main__":
    success = run_master_test_suite()
    sys.exit(0 if success else 1)
