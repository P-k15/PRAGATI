import firebase_admin
from firebase_admin import credentials, firestore
import os
import logging

logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK only once
def initialize_firebase():
    """
    Initialize Firebase Admin SDK with the service account credentials.
    Returns the Firestore client or None if initialization fails.
    """
    try:
        # Check if Firebase app is already initialized
        try:
            app = firebase_admin.get_app()
            logger.info("Firebase app already initialized")
        except ValueError:
            # Firebase app not initialized, initialize it
            cred_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY_PATH")
            if not cred_path:
                logger.error("FIREBASE_SERVICE_ACCOUNT_KEY_PATH environment variable is not set")
                return None

            if not os.path.exists(cred_path):
                logger.error(f"Firebase service account key file not found at: {cred_path}")
                return None

            # Debug: print the cred_path and check if it's quoted
            logger.debug(f"cred_path: {cred_path}")
            logger.debug(f"cred_path repr: {repr(cred_path)}")

            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            logger.info("Firebase app initialized successfully")

        # Return the Firestore client
        return firestore.client()
    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {e}")
        return None

# Initialize the Firestore client
db = initialize_firebase()
if db is None:
    logger.warning("Firebase is not available. Some features will be disabled.")
