import os
import json

env_path = './.env'
env_vars = {}
with open(env_path, 'r') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#'):
            if '=' in line:
                k, v = line.split('=', 1)
                k = k.strip()
                v = v.strip()
                # Remove surrounding quotes if present
                if len(v) >= 2 and v[0] == '"' and v[-1] == '"':
                    v = v[1:-1]
                env_vars[k] = v

# Build service account dict
sa = {
    'type': 'service_account',
    'project_id': env_vars.get('FIREBASE_PROJECT_ID', ''),
    'private_key_id': env_vars.get('FIREBASE_PRIVATE_KEY_ID', ''),
    # Handle private key: replace \n with actual newlines
    'private_key': env_vars.get('FIREBASE_PRIVATE_KEY', '').replace('\\n', '\n'),
    'client_email': env_vars.get('FIREBASE_CLIENT_EMAIL', ''),
    'client_id': env_vars.get('FIREBASE_CLIENT_ID', ''),
    'auth_uri': env_vars.get('FIREBASE_AUTH_URI', 'https://accounts.google.com/o/oauth2/auth'),
    'token_uri': env_vars.get('FIREBASE_TOKEN_URI', 'https://oauth2.googleapis.com/token'),
    'auth_provider_x509_cert_url': env_vars.get('FIREBASE_AUTH_PROVIDER_X509_CERT_URL', 'https://www.googleapis.com/oauth2/v1/certs'),
    'client_x509_cert_url': env_vars.get('FIREBASE_CLIENT_X509_CERT_URL', '')
}

# Write to serviceAccountKey.json
output_path = './serviceAccountKey.json'
with open(output_path, 'w') as f:
    json.dump(sa, f, indent=2)

# Verify the fix
with open(output_path, 'r') as f:
    data = json.load(f)
pk = data['private_key']
if '\n' in pk:
    print("ERROR: Still contains literal backslash-n")
else:
    print("SUCCESS: Private key contains actual newlines")
    # Count newlines
    newline_count = pk.count('\n')
    print("Private key has " + str(newline_count) + " newline characters")
