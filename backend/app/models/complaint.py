# This is a placeholder for the complaint model.
# Since we are using Firebase Firestore, we don't have a traditional ORM model.
# However, we can define a class to represent the complaint entity for clarity.

class Complaint:
    def __init__(
        self,
        id: str,
        citizen_id: str,
        description: str,
        location: str,
        status: str = "SUBMITTED",
        category: str = None,
        subcategory: str = None,
        severity: str = None,
        priority: str = None,
        department: str = None,
        sla_hours: int = None,
        summary: str = None,
        # SLA fields
        sla_deadline: str = None,  # ISO format string
        # SLA Monitoring & Escalation (Phase 5.3)
        sla_status: str = None,  # ON_TRACK, DUE_SOON, OVERDUE, RESOLVED
        escalation_level: int = 0,
        escalated: bool = False,
        escalated_at: str = None,  # ISO format string
        escalation_reason: str = None,
        previous_assigned_officer: str = None,
        # Timestamps
        created_at: str = None,  # ISO format string
        updated_at: str = None,  # ISO format string
        resolved_at: str = None,  # ISO format string
    ):
        self.id = id
        self.citizen_id = citizen_id
        self.description = description
        self.location = location
        self.status = status
        self.category = category
        self.subcategory = subcategory
        self.severity = severity
        self.priority = priority
        self.department = department
        self.sla_hours = sla_hours
        self.summary = summary
        self.sla_deadline = sla_deadline
        self.sla_status = sla_status
        self.escalation_level = escalation_level
        self.escalated = escalated
        self.escalated_at = escalated_at
        self.escalation_reason = escalation_reason
        self.previous_assigned_officer = previous_assigned_officer
        self.created_at = created_at
        self.updated_at = updated_at
        self.resolved_at = resolved_at

    def to_dict(self):
        """Convert the complaint object to a dictionary for Firestore."""
        return {
            "citizen_id": self.citizen_id,
            "description": self.description,
            "location": self.location,
            "status": self.status,
            "category": self.category,
            "subcategory": self.subcategory,
            "severity": self.severity,
            "priority": self.priority,
            "department": self.department,
            "sla_hours": self.sla_hours,
            "summary": self.summary,
            "sla_deadline": self.sla_deadline,
            "sla_status": self.sla_status,
            "escalation_level": self.escalation_level,
            "escalated": self.escalated,
            "escalated_at": self.escalated_at,
            "escalation_reason": self.escalation_reason,
            "previous_assigned_officer": self.previous_assigned_officer,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "resolved_at": self.resolved_at,
        }

    @classmethod
    def from_dict(cls, complaint_id: str, data: dict):
        """Create a Complaint instance from a Firestore document."""
        return cls(
            id=complaint_id,
            citizen_id=data.get("citizen_id"),
            description=data.get("description"),
            location=data.get("location"),
            status=data.get("status", "SUBMITTED"),
            category=data.get("category"),
            subcategory=data.get("subcategory"),
            severity=data.get("severity"),
            priority=data.get("priority"),
            department=data.get("department"),
            sla_hours=data.get("sla_hours"),
            summary=data.get("summary"),
            sla_deadline=data.get("sla_deadline"),
            sla_status=data.get("sla_status"),
            escalation_level=data.get("escalation_level", 0),
            escalated=data.get("escalated", False),
            escalated_at=data.get("escalated_at"),
            escalation_reason=data.get("escalation_reason"),
            previous_assigned_officer=data.get("previous_assigned_officer"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            resolved_at=data.get("resolved_at"),
        )