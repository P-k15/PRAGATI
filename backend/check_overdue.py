import requests

BASE_URL = 'http://localhost:8000/api/v1'

def get_complaints(skip=0, limit=100):
    response = requests.get(f'{BASE_URL}/complaints/', params={'skip': skip, 'limit': limit})
    if response.status_code == 200:
        return response.json()
    else:
        print(f'Error: {response.status_code}')
        return None

def main():
    # Get all complaints (assuming less than 200)
    complaints = get_complaints(limit=200)
    if not complaints:
        print('Failed to fetch complaints')
        return

    print(f'Total complaints fetched: {len(complaints)}')

    overdue_count = 0
    overdue_not_escalated = 0
    overdue_escalated = 0

    for c in complaints:
        sla_status = c.get('sla_status')
        escalated = c.get('escalated', False)
        if sla_status == 'OVERDUE':
            overdue_count += 1
            if escalated:
                overdue_escalated += 1
            else:
                overdue_not_escalated += 1
                print('Overdue but not escalated: ID {}, Department: {}, SLA status: {}, Escalated: {}'.format(
                    c.get('id'), c.get('department'), sla_status, escalated))

    print(f'Overdue complaints: {overdue_count}')
    print(f'Overdue and escalated: {overdue_escalated}')
    print(f'Overdue but NOT escalated: {overdue_not_escalated}')

    if overdue_not_escalated == 0 and overdue_count > 0:
        print('All overdue complaints are already escalated.')
    elif overdue_count == 0:
        print('No overdue complaints.')
    else:
        print('There are overdue complaints that have not been escalated.')

if __name__ == '__main__':
    main()