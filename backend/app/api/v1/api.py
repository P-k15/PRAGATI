from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app import models
from app.schemas.user import Token, TokenData, User, UserCreate, UserLogin
from app.schemas.complaint import Complaint, ComplaintCreate, ComplaintUpdate
from app.core.security import get_password_hash, authenticate_user, get_fake_users_db, create_access_token
from app.core.config import settings
from app.services.ai_service import ai_service
from app.services.routing_service import routing_service
from app.services import sla_service
from app.core.firebase import db
import logging
import os
from datetime import datetime, timedelta, timezone

# Helper functions for Firebase operations
def get_complaint_ref(complaint_id: str):
    return db.collection("complaints").document(complaint_id)

def get_user_ref(user_id: str):
    return db.collection("users").document(user_id)

router = APIRouter()

# Authentication endpoints
@router.post("/auth/login", response_model=Token)
def login(user_credentials: UserLogin):
    fake_db = get_fake_users_db()
    user = authenticate_user(
        fake_db, user_credentials.email, user_credentials.password
    )
    if not user:
        # Check Firestore for registered user
        try:
            users_query = db.collection("users").where("email", "==", user_credentials.email).stream()
            user_doc = next(users_query, None)
            if user_doc:
                user_data = user_doc.to_dict()
                user = {"email": user_data["email"], "role": user_data.get("role", "citizen")}
        except Exception:
            pass

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user["email"]})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/auth/register", response_model=User)
def register(user_in: UserCreate):
    created_at = datetime.utcnow().isoformat()
    user_dict = {
        "id": f"user_{int(datetime.utcnow().timestamp())}",
        "email": user_in.email,
        "full_name": user_in.full_name,
        "role": user_in.role,
        "is_active": True,
        "created_at": created_at,
    }
    try:
        db.collection("users").document(user_dict["id"]).set(user_dict)
    except Exception as e:
        print(f"Firestore user registration warning: {e}")
    return user_dict

# Complaint endpoints
@router.post("/complaints/", response_model=Complaint)
async def create_complaint(
    complaint: ComplaintCreate,
    # In a real app, you would get the current user from the token
    # For MVP, fallback to default citizen ID if not specified in complaint payload
    citizen_id: str = "citizen_example_uid",
):
    # Get AI analysis from NVIDIA Nemotron API
    try:
        ai_analysis = await ai_service.analyze_complaint(complaint.description)
        ai_analysis_dict = ai_analysis.dict()
        ai_source = "nvidia"
    except Exception as e:
        print(f"AI service failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI analysis service temporarily unavailable"
        )

    # Calculate SLA deadline
    created_at = datetime.utcnow()
    sla_deadline = created_at + timedelta(hours=ai_analysis_dict["sla_hours"])

    effective_citizen_id = complaint.citizen_id if (hasattr(complaint, 'citizen_id') and complaint.citizen_id) else citizen_id

    complaint_data = complaint.dict()
    complaint_data.update({
        "citizen_id": effective_citizen_id,
        "status": "AI_PROCESSED",  # Status after successful AI analysis
        "ai_source": ai_source,
        "latitude": None,  # Not implemented yet
        "longitude": None,  # Not implemented yet
        "assigned_officer": None,  # Will be set by routing if officer available
        "sla_hours": ai_analysis_dict["sla_hours"],
        "sla_deadline": sla_deadline.isoformat(),  # Store as ISO string
        "summary": ai_analysis_dict["summary"],
        "category": ai_analysis_dict["category"],
        "subcategory": ai_analysis_dict["subcategory"],
        "severity": ai_analysis_dict["severity"],
        "priority": ai_analysis_dict["priority"],
        "department": ai_analysis_dict["department"],
        # AI Decision Engine fields (Phase 5.1)
        "recommended_action": ai_analysis_dict["recommended_action"],
        "confidence": ai_analysis_dict["confidence"],
        "resolved_at": None,  # Not resolved yet
        "created_at": created_at.isoformat(),
        "updated_at": created_at.isoformat(),
    })

    # Try to automatically assign complaint to an officer using routing service
    department = ai_analysis_dict["department"]
    complaint_id_temp = None  # Will be set after Firestore write

    try:
        # Select officer based on department and workload
        selected_officer = await routing_service.select_officer(department, complaint_id_temp or "temp")

        if selected_officer:
            # Officer found, update complaint data for assignment
            officer_id = selected_officer["id"]
            complaint_data.update({
                "assigned_officer": officer_id,
                "status": "ASSIGNED",  # Change status to ASSIGNED
                "assigned_at": created_at.isoformat(),
                "routing_source": "rule_based",
                "routing_reason": f"Assigned to available {department} officer with lowest active workload."
            })

            # Add to Firestore with assignment data
            _, doc_ref = db.collection("complaints").add(complaint_data)
            complaint_data["id"] = doc_ref.id
            complaint_id_temp = complaint_data["id"]

            # Update officer's active complaint count
            await routing_service.update_officer_workload(officer_id, increment=True)
        else:
            # No eligible officer found, keep as AI_PROCESSED
            _, doc_ref = db.collection("complaints").add(complaint_data)
            complaint_data["id"] = doc_ref.id

    except Exception as e:
        # If routing fails, fall back to AI_PROCESSED status
        print(f"Routing service failed: {str(e)}")
        _, doc_ref = db.collection("complaints").add(complaint_data)
        complaint_data["id"] = doc_ref.id

    # Calculate initial SLA status
    sla_info = sla_service.calculate_sla_status(complaint_data)
    complaint_data["sla_status"] = sla_info["sla_status"]

    return complaint_data

@router.get("/complaints/", response_model=List[Complaint])
def read_complaints(
    skip: int = 0,
    limit: int = 100,
    # In a real app, you would filter by current user's role and ID
    citizen_id: Optional[str] = None,  # For citizens, show their complaints
    status: Optional[str] = None,  # Filter by status
):
    complaints_ref = db.collection("complaints")

    # Get documents with pagination
    # For mock, we'll get all and then filter/paginate
    all_docs = []
    complaints_collection = db.collection("complaints")
    if hasattr(complaints_collection, 'documents'):
        # It's our mock
        for doc_id, doc_data in complaints_collection.documents.items():
            doc_data_with_id = doc_data.copy()
            doc_data_with_id["id"] = doc_id
            all_docs.append(doc_data_with_id)
    else:
        # It's real Firestore
        complaints = complaints_collection.stream()
        for doc in complaints:
            doc_data = doc.to_dict()
            doc_data["id"] = doc.id
            all_docs.append(doc_data)

    # Apply filters manually for mock
    if citizen_id:
        all_docs = [doc for doc in all_docs if doc.get("citizen_id") == citizen_id]
    if status:
        all_docs = [doc for doc in all_docs if doc.get("status") == status]

    # Apply pagination
    paginated_docs = all_docs[skip:skip+limit]

    return paginated_docs

@router.get("/complaints/{complaint_id}", response_model=Complaint)
def read_complaint(complaint_id: str):
    doc = get_complaint_ref(complaint_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Complaint not found")
    complaint_data = doc.to_dict()
    complaint_data["id"] = doc.id
    return complaint_data

@router.put("/complaints/{complaint_id}", response_model=Complaint)
def update_complaint(
    complaint_id: str,
    complaint_update: ComplaintUpdate,
    # In a real app, you would check permissions (officer can update, citizen can only update certain fields)
):
    doc_ref = get_complaint_ref(complaint_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Complaint not found")

    update_data = complaint_update.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow().isoformat()

    # If status is being set to RESOLVED, set resolved_at and sla_status to RESOLVED
    if update_data.get('status') == 'RESOLVED':
        update_data['resolved_at'] = datetime.utcnow().isoformat()
        update_data['sla_status'] = 'RESOLVED'

    doc_ref.update(update_data)

    # Return updated complaint
    updated_doc = doc_ref.get()
    complaint_data = updated_doc.to_dict()
    complaint_data["id"] = updated_doc.id
    return complaint_data

@router.patch("/complaints/{complaint_id}/status")
async def update_complaint_status(complaint_id: str, status_update: dict):
    # Validate the status
    allowed_statuses = ["SUBMITTED", "AI_PROCESSED", "ASSIGNED", "IN_PROGRESS", "RESOLVED"]
    new_status = status_update.get("status")
    if not new_status or new_status not in allowed_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of {allowed_statuses}"
        )

    doc_ref = get_complaint_ref(complaint_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Complaint not found")

    update_data = {
        "status": new_status,
        "updated_at": datetime.utcnow().isoformat()
    }

    # If status is being set to RESOLVED, set resolved_at and sla_status to RESOLVED
    if new_status == "RESOLVED":
        update_data["resolved_at"] = datetime.utcnow().isoformat()
        update_data["sla_status"] = "RESOLVED"

    doc_ref.update(update_data)

    # Return updated complaint
    updated_doc = doc_ref.get()
    complaint_data = updated_doc.to_dict()
    complaint_data["id"] = updated_doc.id
    return complaint_data

@router.patch("/complaints/{complaint_id}/assign")
async def assign_complaint_officer(complaint_id: str, assignment: dict):
    officer_id = assignment.get("officer_id")
    if not officer_id or not isinstance(officer_id, str) or officer_id.strip() == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid officer_id. Must be a non-empty string."
        )

    doc_ref = get_complaint_ref(complaint_id)
    doc = doc_ref.get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Complaint not found")

    update_data = {
        "assigned_officer": officer_id,
        "status": "ASSIGNED",
        "updated_at": datetime.utcnow().isoformat()
    }

    doc_ref.update(update_data)

    # Return updated complaint
    updated_doc = doc_ref.get()
    complaint_data = updated_doc.to_dict()
    complaint_data["id"] = updated_doc.id
    return complaint_data

# SLA Monitoring & Escalation Endpoint
@router.post("/complaints/check-sla")
async def check_sla():
    """
    Check SLA status for all unresolved complaints, update sla_status, and escalate overdue complaints.
    Returns a summary of the check.
    """
    complaints_ref = db.collection("complaints")
    # Fetch all complaints (in a real app, we might want to limit to unresolved ones for efficiency)
    # We'll fetch all and then filter unresolved in memory for simplicity.
    # For a large dataset, we would use Firestore queries.
    complaints = complaints_ref.stream()

    checked = 0
    on_track = 0
    due_soon = 0
    overdue = 0
    resolved = 0
    newly_escalated = 0

    current_time = datetime.now(timezone.utc)

    for complaint_doc in complaints:
        complaint_data = complaint_doc.to_dict()
        complaint_data["id"] = complaint_doc.id

        # Skip if we don't have an sla_deadline (shouldn't happen for AI processed complaints, but just in case)
        if not complaint_data.get("sla_deadline"):
            continue

        checked += 1

        # Calculate current SLA status
        sla_info = sla_service.calculate_sla_status(complaint_data)
        sla_status = sla_info["sla_status"]

        # Determine if we need to update the sla_status in Firestore
        update_needed = False
        update_data = {"updated_at": current_time.isoformat()}

        # Only update sla_status if it has changed or if we are setting it for the first time
        if complaint_data.get("sla_status") != sla_status:
            update_data["sla_status"] = sla_status
            update_needed = True

        # Check if the complaint is overdue and should be escalated
        if sla_status == "OVERDUE" and not complaint_data.get("escalated", False):
            # Escalate the complaint
            escalated_data = sla_service.escalate_complaint(complaint_data)
            # Update the escalation fields
            update_data.update({
                "escalated": escalated_data["escalated"],
                "escalation_level": escalated_data["escalation_level"],
                "escalated_at": escalated_data["escalated_at"],
                "escalation_reason": escalated_data["escalation_reason"],
                "previous_assigned_officer": escalated_data.get("previous_assigned_officer")
            })
            update_needed = True
            newly_escalated += 1

        # If we have updates, apply them to Firestore
        if update_needed:
            complaint_doc.reference.update(update_data)
            # Update the local complaint_data with the updates for counting
            complaint_data.update(update_data)

        # Count the complaint based on its updated sla_status
        current_sla_status = complaint_data.get("sla_status")
        if current_sla_status == "ON_TRACK":
            on_track += 1
        elif current_sla_status == "DUE_SOON":
            due_soon += 1
        elif current_sla_status == "OVERDUE":
            overdue += 1
        elif current_sla_status == "RESOLVED":
            resolved += 1

    return {
        "checked": checked,
        "on_track": on_track,
        "due_soon": due_soon,
        "overdue": overdue,
        "resolved": resolved,
        "newly_escalated": newly_escalated
    }