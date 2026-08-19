import os
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

load_dotenv()

# Initialize Firebase Admin SDK only once
def initialize_firebase():
    try:
        app = firebase_admin.get_app()
        # logger.info("Firebase app already initialized")
    except ValueError:
        cred_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY_PATH")
        if not cred_path:
            raise ValueError("FIREBASE_SERVICE_ACCOUNT_KEY_PATH environment variable is not set")
        if not os.path.exists(cred_path):
            raise ValueError(f"Firebase service account key file not found at: {cred_path}")
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        # logger.info("Firebase app initialized successfully")
    return firestore.client()

# Initialize logger
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_officers():
    db = initialize_firebase()
    officers_ref = db.collection("officers")

    # Define officers to seed
    officers_to_seed = [
        {
            "id": "officer_001",
            "name": "Officer A",
            "department": "Electrical Maintenance",
            "available": True,
            "active_complaints": 2
        },
        {
            "id": "officer_002",
            "name": "Officer B",
            "department": "Electrical Maintenance",
            "available": True,
            "active_complaints": 1
        },
        {
            "id": "officer_003",
            "name": "Officer C",
            "department": "Sanitation",
            "available": True,
            "active_complaints": 0
        },
        {
            "id": "officer_004",
            "name": "Officer D",
            "department": "Sanitation",
            "available": True,
            "active_complaints": 3
        },
        {
            "id": "officer_005",
            "name": "Officer E",
            "department": "Water Works",
            "available": True,
            "active_complaints": 4
        },
        {
            "id": "officer_006",
            "name": "Officer F",
            "department": "Water Works",
            "available": True,
            "active_complaints": 0
        },
        {
            "id": "officer_007",
            "name": "Officer G",
            "department": "Road Maintenance",
            "available": True,
            "active_complaints": 1
        },
        {
            "id": "officer_008",
            "name": "Officer H",
            "department": "Road Maintenance",
            "available": True,
            "active_complaints": 2
        }
    ]

    for officer_data in officers_to_seed:
        officer_id = officer_data["id"]
        # Check if officer already exists
        doc_ref = officers_ref.document(officer_id)
        doc = doc_ref.get()
        if doc.exists:
            logger.info(f"Officer {officer_id} already exists, skipping.")
            # Optionally, you can update the officer data if needed
            # But for idempotency, we'll skip updates to avoid overwriting changes
            continue
        else:
            # Create new officer
            doc_ref.set(officer_data)
            logger.info(f"Created officer: {officer_id}")

    logger.info("Officer seeding completed.")

if __name__ == "__main__":
    seed_officers()