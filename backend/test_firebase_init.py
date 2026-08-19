import os
import firebase_admin
from firebase_admin import credentials, firestore
import json

# Load the service account key from the file we created
cred_path = os.path.join(os.getcwd(), 'serviceAccountKey.json')
print(f"Using service account key at: {cred_path}")

try:
    # Try to load the certificate from the file
    cred = credentials.Certificate(cred_path)
    print("Certificate loaded successfully from file.")
except Exception as e:
    print(f"Failed to load certificate from file: {e}")
    # Try loading from a dictionary
    with open(cred_path, 'r') as f:
        cred_dict = json.load(f)
    try:
        cred = credentials.Certificate(cred_dict)
        print("Certificate loaded successfully from dictionary.")
    except Exception as e2:
        print(f"Failed to load certificate from dictionary: {e2}")
        exit(1)

# Try to initialize the app
try:
    firebase_admin.initialize_app(cred)
    print("Firebase app initialized successfully.")
except Exception as e:
    print(f"Failed to initialize Firebase app: {e}")
    exit(1)

# Try to get the Firestore client
try:
    db = firestore.client()
    print("Firestore client obtained successfully.")
except Exception as e:
    print(f"Failed to get Firestore client: {e}")
    exit(1)

# Try a simple operation (list collections) to see if we can connect
try:
    collections = db.collections()
    # Just try to iterate once to see if it works
    for collection in collections:
        print(f"Found collection: {collection.id}")
        break
    print("Firestore connection test successful.")
except Exception as e:
    print(f"Firestore connection test failed: {e}")
    exit(1)
