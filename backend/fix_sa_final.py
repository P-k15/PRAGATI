import os
import json

# Read .env file
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

# Get the raw private key string from .env (after removing quotes)
raw_private_key = env_vars.get('FIREBASE_PRIVATE_KEY', '')
print(f"Raw private key length: {len(raw_private_key)}")
print(f"First 100 chars of raw private key: {repr(raw_private_key[:100])}")

# The raw string contains backslash-n as two characters: '\' and 'n'
# We want to replace each occurrence of the two-character sequence backslash-n with a newline character.
# In the raw string, the backslash is represented as '\' (one backslash) and 'n' as 'n'.
# So we look for the two-character string: '\n' (which is a backslash followed by n).
# In Python, to represent a backslash in a string literal, we use '\\', but when the string is already in memory,
# the backslash is a single character. So we can do:
fixed_private_key = raw_private_key.replace('\\n', '\n')
# Alternatively, we can use:
# fixed_private_key = raw_private_key.replace('\' + 'n', '\n') but that is the same.

print(f"Fixed private key length: {len(fixed_private_key)}")
print(f"First 100 chars of fixed private key: {repr(fixed_private_key[:100])}")
print(f"Number of newline characters in fixed key: {fixed_private_key.count(chr(10))}")

# Build service account dict
sa = {
    'type': 'service_account',
    'project_id': env_vars.get('FIREBASE_PROJECT_ID', ''),
    'private_key_id': env_vars.get('FIREBASE_PRIVATE_KEY_ID', ''),
    'private_key': fixed_private_key,
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

print(f"Service account key written to {output_path}")

# Quick verification: try to load the certificate
try:
    from firebase_admin import credentials
    cred = credentials.Certificate(output_path)
    print("Certificate loaded successfully!")
except Exception as e:
    print(f"Failed to load certificate: {e}")
