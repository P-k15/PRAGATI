# PRAGATI — Claude Code Project Context

## Project Identity

Project name: PRAGATI

PRAGATI is a civic grievance/complaint management system built for our college internal hackathon.

The system has:
- Flutter mobile frontend
- FastAPI Python backend
- Firestore database
- NVIDIA Nemotron AI for grievance classification/processing
- Citizen authentication
- Officer authentication
- Automated complaint routing
- Complaint lifecycle/state management

IMPORTANT:
- The project is already functional.
- Do NOT rebuild existing functionality unnecessarily.
- Before modifying anything, inspect the existing implementation.
- Preserve existing working APIs, schemas, database behavior, authentication, routing, and frontend flows unless the requested feature explicitly requires changes.

---

# Architecture

## Backend

Location:
backend/

Technology:
- Python
- FastAPI
- Firestore
- Pydantic
- Uvicorn

Important structure:

backend/app/
├── api/
│   └── v1/
├── core/
├── schemas/
├── services/
└── main.py

Important backend services include:
- AI service
- Complaint handling
- Automated routing
- Authentication/security

---

# Frontend

Location:
frontend/

Technology:
- Flutter
- Dart

Important files:

frontend/lib/main.dart
frontend/lib/services/api_service.dart
frontend/lib/models/complaint_model.dart

The Flutter application contains:
- Citizen Portal
- Officer Portal
- Citizen registration/login
- Officer login
- Citizen dashboard
- Complaint submission
- My Complaints
- Complaint tracking
- Bottom navigation
- API integration with FastAPI

---

# Authentication

Citizen registration endpoint:

POST /api/v1/auth/register

Citizen login endpoint:

POST /api/v1/auth/login

The backend supports:
1. Demo accounts
2. Firestore-registered users

Citizen registration stores users in the Firestore `users` collection.

User login schema:

UserLogin:
- email
- password

Password hashing uses:

pbkdf2_sha256

Do NOT revert to bcrypt/passlib bcrypt unless there is a specific reason, because bcrypt caused a Python 3.11 / Windows 72-byte buffer issue.

---

# Complaint System

Complaint schema supports:

citizen_id: Optional[str]

The create complaint endpoint must respect a citizen_id supplied by the client.

Do NOT overwrite client-provided citizen_id with a hardcoded/default value.

Complaint lifecycle currently supports:

SUBMITTED
→ AI_PROCESSED
→ ASSIGNED
→ IN_PROGRESS
→ RESOLVED

Invalid state transitions are guarded.

When a complaint reaches RESOLVED:
- resolved_at is automatically recorded as an ISO timestamp.

---

# AI Engine

AI service:

backend/app/services/ai_service.py

AI provider:
NVIDIA Nemotron

Current implementation includes:

- max_tokens = 1024
- JSON extraction
- regex-based key extraction
- malformed JSON recovery
- unescaped newline cleaning
- fallback/default values when AI times out or returns malformed output

IMPORTANT:

The AI layer must fail gracefully.

A temporary NVIDIA API failure, timeout, malformed response, or invalid JSON must NOT crash the complaint creation endpoint.

Do not remove the existing fallback behavior.

---

# Automated Officer Routing

The project contains an automated routing engine.

Purpose:

Automatically select an officer based on:
- department
- officer availability
- workload

Behavior:

If a suitable officer is available:
- complaint is automatically assigned.

If no suitable officer is available:
- complaint remains/falls back to AI_PROCESSED.

Manual officer assignment must continue to work.

Do NOT break existing manual assignment functionality while modifying automated routing.

---

# Flutter API Configuration

Frontend API service:

frontend/lib/services/api_service.dart

Default backend:

http://127.0.0.1:8000

The API service automatically handles `/api/v1` formatting.

For physical Android USB testing:

adb reverse tcp:8000 tcp:8000

This allows the Android device to access the local backend.

---

# Flutter Navigation

The application contains:

Citizen Portal:
- Sign In
- Register

Officer Portal:
- Sign In

Citizen dashboard route:

/citizen-home

Do NOT remove or rename this route without checking all references.

Citizen dashboard includes:

- Home
- Submit
- My Complaints

There is also complaint tracking by complaint ID.

---

# Flutter Null Safety

File:

frontend/lib/models/complaint_model.dart

ComplaintModel.fromJson was rewritten to safely handle null/malformed API values.

Use patterns such as:

?.toString() ?? ''

DateTime.tryParse()

numeric type checking

IMPORTANT:

Do not reintroduce unsafe casts such as:

json['field'] as String

unless the field is guaranteed to be non-null.

---

# Branding

Flutter launcher icon configuration exists in:

frontend/pubspec.yaml

Icon asset:

frontend/assets/icon.png.png

flutter_launcher_icons is already configured.

Generated Android launcher icons already exist across:

mipmap-mdpi
mipmap-hdpi
mipmap-xhdpi
mipmap-xxhdpi
mipmap-xxxhdpi

Do not unnecessarily regenerate or replace branding.

---

# Testing

Master backend test:

backend/test_master_suite.py

Current status:

15/15 tests passing.

The test suite covers:

1. System health
2. Citizen registration
3. Citizen authentication
4. Officer authentication
5. Invalid password protection
6. NVIDIA AI grievance classification
7. Automated officer routing
8. Complaint details
9. Citizen complaint filtering
10. State transitions
11. resolved_at timestamp
12. Manual officer assignment
13. Invalid state transition protection
14. Additional complaint workflow checks
15. End-to-end workflow behavior

IMPORTANT:

Before making major backend changes, run:

python test_master_suite.py

After changes, run it again.

Do not consider a backend feature complete if existing tests regress.

---

# Flutter Quality

Run:

flutter analyze

Current expected status:

0 errors.

When changing Flutter code:
- preserve null safety
- preserve existing navigation
- preserve API integration
- avoid breaking physical-device behavior

---

# Development Commands

## Backend

PowerShell:

cd C:\Users\Lenovo\Desktop\PRAGATI\backend

.\venv\Scripts\Activate.ps1

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

## Backend tests

cd C:\Users\Lenovo\Desktop\PRAGATI\backend

python test_master_suite.py

## Flutter

cd C:\Users\Lenovo\Desktop\PRAGATI\frontend

flutter analyze

flutter run

## Physical Android device

adb reverse tcp:8000 tcp:8000

flutter run

---

# Development Rules

Before implementing any requested feature:

1. Inspect the existing relevant files.
2. Understand the current architecture.
3. Reuse existing services/functions/models where possible.
4. Do not duplicate existing functionality.
5. Do not rewrite working modules unnecessarily.
6. Preserve existing API contracts.
7. Preserve existing database structure unless a migration/change is required.
8. Preserve existing authentication.
9. Preserve existing AI fallback behavior.
10. Preserve automated routing.
11. Preserve manual officer assignment.
12. Run relevant tests after changes.
13. Report exactly which files were changed.
14. Report any tests run and their results.

When fixing a bug:
- Find the root cause first.
- Make the smallest safe change.
- Do not introduce unrelated refactoring.

When adding a feature:
- First identify how it fits into the current architecture.
- Implement backend/API changes first if necessary.
- Then update Flutter integration.
- Add/update tests.
- Verify the complete flow.

---

# Current Project Status

The project already has:

✅ Citizen registration
✅ Citizen login
✅ Officer login
✅ Firestore user persistence
✅ Secure password hashing
✅ AI grievance classification
✅ AI malformed-response fallback
✅ Complaint creation
✅ Citizen ID tracking
✅ Complaint retrieval
✅ Citizen complaint filtering
✅ Automated officer routing
✅ Workload-based assignment
✅ Manual officer assignment
✅ Complaint state machine
✅ resolved_at timestamp
✅ Flutter Citizen Portal
✅ Flutter Officer Portal
✅ Complaint submission
✅ Complaint tracking
✅ Bottom navigation
✅ Null-safe complaint parsing
✅ Custom launcher icon
✅ Backend master test suite
✅ Flutter static analysis

Backend master test status:
15/15 PASS

Flutter analyze:
0 errors

---

# Critical Instruction

PRAGATI is an existing working project.

Do not assume the project is empty or incomplete.

Always inspect the current implementation before coding.

If a requested feature overlaps with existing functionality, extend the existing implementation instead of creating a parallel system.

Do not remove working functionality merely to simplify implementation.

If you believe an architectural change is necessary, explain why before making a large refactor.