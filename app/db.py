import os
import firebase_admin
from firebase_admin import initialize_app
from google.cloud import firestore

# Use emulator: initialize without credentials, just the projectId
PROJECT_ID = os.getenv("GCLOUD_PROJECT", "demo-project")
if not firebase_admin._apps:
    initialize_app(options={"projectId": PROJECT_ID})

# Firestore client (automatically uses emulator if FIRESTORE_EMULATOR_HOST is set)
db = firestore.Client(project=PROJECT_ID)
