import os, json
with open('.env', 'r') as f:
    lines = f.readlines()
data = {}
for line in lines:
    line = line.strip()
    if line and not line.startswith('#'):
        if '=' in line:
            k, v = line.split('=', 1)
            data[k.strip()] = v.strip()
# Build service account dict
sa = {
    'type': 'service_account',
    'project_id': data.get('FIREBASE_PROJECT_ID', ''),
    'private_key_id': data.get('FIREBASE_PRIVATE_KEY_ID', ''),
    'private_key': data.get('FIREBASE_PRIVATE_KEY', '').replace('\n', '\n'),
    'client_email': data.get('FIREBASE_CLIENT_EMAIL', ''),
    'client_id': data.get('FIREBASE_CLIENT_ID', ''),
    'auth_uri': data.get('FIREBASE_AUTH_URI', 'https://accounts.google.com/o/oauth2/auth'),
    'token_uri': data.get('FIREBASE_TOKEN_URI', 'https://oauth2.googleapis.com/token'),
    'auth_provider_x509_cert_url': data.get('FIREBASE_AUTH_PROVIDER_X509_CERT_URL', 'https://www.googleapis.com/oauth2/v1/certs'),
    'client_x509_cert_url': data.get('FIREBASE_CLIENT_X509_CERT_URL', '')
}
with open('serviceAccountKey.json', 'w') as f:
    json.dump(sa, f, indent=2)
print('Created serviceAccountKey.json')
