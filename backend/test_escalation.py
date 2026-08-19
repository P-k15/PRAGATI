import requests
import json
from datetime import datetime, timedelta

BASE_URL = 'http://localhost:8000/api/v1'

def post_complaint(description, location, citizen_id='citizen_test'):
    payload = {
        'description': description,
        'location': location,
        'citizen_id': citizen_id
    }
    response = requests.post(f'{BASE_URL}/complaints/', json=payload)
    return response.json(), response.status_code

def get_complaint(complaint_id):
    response = requests.get(f'{BASE_URL}/complaints/{complaint_id}')
    return response.json(), response.status_code

def update_complaint(complaint_id, update_data):
    response = requests.patch(f'{BASE_URL}/complaints/{complaint_id}', json=update_data)
    return response.json(), response.status_code

def run_sla_check():
    response = requests.post(f'{BASE_URL}/complaints/check-sla')
    return response.json(), response.status_code

# Create a complaint
desc = 'Test complaint for escalation'
loc = 'Test Location'
result, status = post_complaint(desc, loc)
if status != 200:
    print(f'Failed to create complaint: {result}')
    exit(1)

complaint_id = result.get('id')
print(f'Created complaint ID: {complaint_id}')
print(f'Initial data: {json.dumps(result, indent=2)}')

# Get the complaint to see current sla_deadline
comp, status = get_complaint(complaint_id)
if status != 200:
    print(f'Failed to get complaint: {comp}')
    exit(1)

print(f'Current complaint: {json.dumps(comp, indent=2)}')

# Set sla_deadline to be in the past (e.g., 1 hour ago)
past_time = datetime.utcnow() - timedelta(hours=1)
update_data = {
    'sla_deadline': past_time.isoformat()
}
# Also ensure status is not RESOLVED
update_data['status'] = comp.get('status', 'AI_PROCESSED')

print(f'Updating complaint with sla_deadline in the past: {past_time.isoformat()}')
update_result, update_status = update_complaint(complaint_id, update_data)
if update_status != 200:
    print(f'Failed to update complaint: {update_result}')
    exit(1)

print(f'Update result: {json.dumps(update_result, indent=2)}')

# Wait a moment
import time
time.sleep(1)

# Run SLA check
print('Running SLA check...')
sla_result, sla_status = run_sla_check()
if sla_status != 200:
    print(f'SLA check failed: {sla_result}')
else:
    print(f'SLA check result: {json.dumps(sla_result, indent=2)}')

# Get complaint again to see if escalated
comp_after, status = get_complaint(complaint_id)
if status != 200:
    print(f'Failed to get complaint after SLA check: {comp_after}')
else:
    print(f'Complaint after SLA check: {json.dumps(comp_after, indent=2)}')