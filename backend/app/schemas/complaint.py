from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ComplaintBase(BaseModel):
    description: str = Field(..., min_length=1, max_length=500)
    location: str = Field(..., min_length=1, max_length=200)
    citizen_id: Optional[str] = None

class ComplaintCreate(ComplaintBase):
    pass

class ComplaintInDBBase(ComplaintBase):
    id: str
    citizen_id: str  # Firebase UID
    status: str
    category: Optional[str] = None
    subcategory: Optional[str] = None
    severity: Optional[str] = None
    priority: Optional[str] = None
    department: Optional[str] = None
    sla_hours: Optional[int] = None
    summary: Optional[str] = None
    # Geolocation
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    # Assignment
    assigned_officer: Optional[str] = None  # Firebase UID
    assigned_at: Optional[datetime] = None  # Timestamp when assigned
    # SLA
    sla_deadline: Optional[datetime] = None
    # Timestamps
    resolved_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    # AI source
    ai_source: Optional[str] = None  # "nvidia" or "mock"
    # AI Decision Engine fields (Phase 5.1)
    recommended_action: Optional[str] = None
    confidence: Optional[float] = None
    # Routing fields (Phase 5.2)
    routing_source: Optional[str] = None  # "rule_based" or "manual"
    routing_reason: Optional[str] = None  # Reason for assignment
    # SLA Monitoring & Escalation (Phase 5.3)
    sla_status: Optional[str] = None  # ON_TRACK, DUE_SOON, OVERDUE, RESOLVED
    escalation_level: Optional[int] = 0
    escalated: Optional[bool] = False
    escalated_at: Optional[datetime] = None
    escalation_reason: Optional[str] = None
    previous_assigned_officer: Optional[str] = None

    class Config:
        from_attributes = True  # Updated from orm_mode for Pydantic v2

class Complaint(ComplaintInDBBase):
    pass

class ComplaintUpdate(BaseModel):
    status: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    severity: Optional[str] = None
    priority: Optional[str] = None
    department: Optional[str] = None
    sla_hours: Optional[int] = None
    summary: Optional[str] = None
    assigned_officer: Optional[str] = None
    assigned_at: Optional[datetime] = None
    # SLA Monitoring & Escalation (Phase 5.3)
    sla_status: Optional[str] = None
    escalation_level: Optional[int] = None
    escalated: Optional[bool] = None
    escalated_at: Optional[datetime] = None
    escalation_reason: Optional[str] = None
    previous_assigned_officer: Optional[str] = None
    # Note: We don't allow updating the description or location via this update for simplicity
    # AI Decision Engine fields
    recommended_action: Optional[str] = None
    confidence: Optional[float] = None
    # Routing fields (Phase 5.2)
    routing_source: Optional[str] = None
    routing_reason: Optional[str] = None