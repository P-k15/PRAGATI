# PRAGATI - Public Redressal & AI-driven Grievance Automation, Tracking & Intelligence

An AI-powered public grievance management platform for Smart India Hackathon.

## Tech Stack

- **Frontend**: Flutter (Dart)
- **Backend**: Python FastAPI
- **AI**: NVIDIA Nemotron model via NVIDIA NIM API (OpenAI-compatible)
- **Database**: Firebase Firestore

## Project Structure

```
PRAGATI/
├── frontend/                 # Flutter application
│   ├── lib/                  # Dart source code
│   ├── test/                 # Test files
│   ├── android/              # Android platform files
│   ├── ios/                  # iOS platform files
│   └── pubspec.yaml          # Flutter dependencies
├── backend/                  # FastAPI backend
│   ├── app/
│   │   ├── api/              # API endpoints
│   │   ├── core/             # Configuration, security
│   │   ├── models/           # Database models
│   │   └── schemas/          # Pydantic schemas
│   ├── requirements.txt      # Python dependencies
│   └── main.py               # Application entry point
└README.md                    # This file
```

## Setup Instructions

### Backend (FastAPI)

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables (create a `.env` file):
   ```
   NVIDIA_API_KEY=your_nvidia_nim_api_key_here
   FIREBASE_PROJECT_ID=your_firebase_project_id
   FIREBASE_SERVICE_ACCOUNT_KEY_PATH=/path/to/your/serviceAccountKey.json
   # Add other Firebase config as needed
   ```

5. Place your Firebase service account key file at the path specified in FIREBASE_SERVICE_ACCOUNT_KEY_PATH
   (Never commit this file to version control - it's already in .gitignore)

6. Run the development server:
   ```bash
   uvicorn app.main:app --reload
   ```
   The API will be available at `http://localhost:8000`

### Frontend (Flutter)

1. Ensure Flutter is installed and configured:
   ```bash
   flutter doctor
   ```

2. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

3. Get dependencies:
   ```bash
   flutter pub get
   ```

4. Run the app on your preferred device/emulator:
   ```bash
   flutter run
   ```

## API Endpoints

- `POST /api/v1/complaints` - Submit a new complaint (triggers NVIDIA Nemotron AI analysis)
- `GET /api/v1/complaints` - List complaints (with filters: status, priority, department)
- `GET /api/v1/complaints/{id}` - Get complaint details
- `PUT /api/v1/complaints/{id}/status` - Update complaint status
- `PATCH /api/v1/complaints/{id}/status` - Update complaint status (alternative endpoint)
- `PATCH /api/v1/complaints/{id}/assign` - Assign complaint to an officer
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration

## Firebase Setup

1. Create a Firebase project at https://console.firebase.google.com/
2. Enable Firestore Database (in Native mode)
3. Enable Authentication (Email/Password for MVP)
4. For backend: Use Firebase Admin SDK with service account
   - Go to Project Settings > Service Accounts
   - Click "Generate new private key" to download the service account JSON file
   - Place this file securely in your backend directory and reference it in .env
5. For frontend: Use Firebase Flutter plugins (to be implemented in later phases)

## Important Security Notes

1. The NVIDIA API key must ONLY exist in the backend environment variables. Never expose it in the Flutter frontend code.
2. The Firebase service account key file must NEVER be committed to version control. It's already listed in .gitignore.
3. All secrets are loaded from environment variables and never hardcoded.

## Phase Completion Status

### Phase 1: Foundation Verification ✅
- Backend server running with working API endpoints
- Flutter frontend passes static analysis
- Dependencies verified and installed

### Phase 2: NVIDIA Nemotron AI Integration ✅
- Real NVIDIA Nemotron API integration completed and verified
- 5 test complaints successfully analyzed by the Nemotron API
- Proper error handling and fallback mechanisms implemented
- API key security verified (no exposure in logs/responses)

### Phase 3: Firebase Firestore Persistence ✅
- Real Firebase Firestore integration completed
- Mock Firestore replaced with real Firebase implementation
- Proper Firebase initialization with service account credentials
- Complaint documents stored with all required fields:
  - complaint_id, user_id, description, location
  - category, subcategory, severity, priority, department, sla_hours, sla_deadline, summary
  - status, assigned_officer, created_at, updated_at, resolved_at
  - ai_source (to distinguish between "nvidia" and "mock")
- Proper status workflow: SUBMITTED → AI_PROCESSED → ASSIGNED → IN_PROGRESS → RESOLVED
- Filtering by status, priority, department implemented
- Security verified: No Firebase credentials exposed

## Current Working Flow

Flutter (Future)
   ↓
FastAPI (Current)
   ↓
Nemotron (Verified Working - Phase 2)
   ↓
Firestore (Verified Working - Phase 3)
   ↓
FastAPI Response
   ↓
Flutter (Future)

## License

This project is for educational/Smart India Hackathon purposes only.