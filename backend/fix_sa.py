import os
import json
import ast

# Read .env
env_vars = {}
with open('.env', 'r') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#'):
            if '=' in line:
                k, v = line.split('=', 1)
                env_vars[k.strip()] = v.strip()

# Build service account dict
sa = {
    'type': 'service_account',
    'project_id': env_vars.get('FIREBASE_PROJECT_ID', ''),
    'private_key_id': env_vars.get('FIREBASE_PRIVATE_KEY_ID', ''),
    # Handle private key specially: it's a quoted string with escape sequences
    'private_key': ast.literal_eval(env_vars.get('FIREBASE_PRIVATE_KEY', '""')),
    'client_email': env_vars.get('FIREBASE_CLIENT_EMAIL', ''),
    'client_id': env_vars.get('FIREBASE_CLIENT_ID', ''),
    'auth_uri': env_vars.get('FIREBASE_AUTH_URI', 'https://accounts.google.com/o/oauth2/auth'),
    'token_uri': env_vars.get('FIREBASE_TOKEN_URI', 'https://oauth2.googleapis.com/token'),
    'auth_provider_x509_cert_url': env_vars.get('FIREBASE_AUTH_PROVIDER_X509_CERT_URL', 'https://www.googleapis.com/oauth2/v1/certs'),
    'client_x509_cert_url': env_vars.get('FIREBASE_CLIENT_X509_CERT_URL', '')
}

# If any of the fields are empty strings, we might want to keep them as empty strings? 
# But Firebase expects them. We'll leave as is.

# Write to serviceAccountKey.json
with open('serviceAccountKey.json', 'w') as f:
    json.dump(sa, f, indent=2)

print("Fixed serviceAccountKey.json created.")
