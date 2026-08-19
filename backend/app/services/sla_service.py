from datetime import datetime, timezone
from typing import Dict, Any, Optional
from app.core.firebase import db
import logging

logger = logging.getLogger(__name__)

class SLAService:
    def __init__(self):
        self.db = db
        self.complaints_collection = "complaints"

    def calculate_sla_status(self, complaint_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate SLA status for a complaint based on current time and sla_deadline.
        Returns a dict with sla_status, escalated, escalation_level, and related fields.
        Does not modify the complaint_data; caller should update as needed.
        """
        now = datetime.utcnow()
        sla_status = "ON_TRACK"  # default
        escalated = complaint_data.get("escalated", False)
        escalation_level = complaint_data.get("escalation_level", 0)
        escalation_reason = complaint_data.get("escalation_reason")
        escalated_at = complaint_data.get("escalated_at")
        previous_assigned_officer = complaint_data.get("previous_assigned_officer")

        # If complaint is resolved, sla_status is RESOLVED
        if complaint_data.get("status") == "RESOLVED":
            sla_status = "RESOLVED"
            # If it was previously escalated, keep those fields
            return {
                "sla_status": sla_status,
                "escalated": escalated,
                "escalation_level": escalation_level,
                "escalation_reason": escalation_reason,
                "escalated_at": escalated_at,
                "previous_assigned_officer": previous_assigned_officer
            }

        sla_deadline_str = complaint_data.get("sla_deadline")
        if not sla_deadline_str:
            # No deadline, cannot determine SLA status
            return {
                "sla_status": "ON_TRACK",
                "escalated": escalated,
                "escalation_level": escalation_level,
                "escalation_reason": escalation_reason,
                "escalated_at": escalated_at,
                "previous_assigned_officer": previous_assigned_officer
            }

        try:
            # sla_deadline is stored as ISO string
            sla_deadline = datetime.fromisoformat(sla_deadline_str.replace("Z", "+00:00"))
        except Exception as e:
            logger.error(f"Error parsing sla_deadline {sla_deadline_str}: {str(e)}")
            return {
                "sla_status": "ON_TRACK",
                "escalated": escalated,
                "escalation_level": escalation_level,
                "escalation_reason": escalation_reason,
                "escalated_at": escalated_at,
                "previous_assigned_officer": previous_assigned_officer
            }

        # Determine SLA status
        if now > sla_deadline:
            sla_status = "OVERDUE"
        else:
            # Calculate remaining time and percentage
            total_sla_seconds = (sla_deadline - datetime.fromisoformat(complaint_data.get("created_at", now.isoformat()).replace("Z", "+00:00"))).total_seconds()
            if total_sla_seconds <= 0:
                # Avoid division by zero
                remaining_percentage = 0
            else:
                remaining_seconds = (sla_deadline - now).total_seconds()
                remaining_percentage = (remaining_seconds / total_sla_seconds) * 100

            if remaining_percentage <= 25:
                sla_status = "DUE_SOON"
            else:
                sla_status = "ON_TRACK"

        # If OVERDUE and not yet escaled, we should escalate
        # Note: actual escalation will be done by the check_sla endpoint or similar
        # Here we just return the status; escalation is a separate action
        return {
            "sla_status": sla_status,
            "escalated": escalated,
            "escalation_level": escalation_level,
            "escalation_reason": escalation_reason,
            "escalated_at": escalated_at,
            "previous_assigned_officer": previous_assigned_officer
        }

    def escalate_complaint(self, complaint_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Return updated fields for escalation.
        Should be called when complaint is OVERDUE and escalated == False.
        """
        now = datetime.utcnow()
        current_level = complaint_data.get("escalation_level", 0)
        new_level = current_level + 1
        return {
            "escalated": True,
            "escalation_level": new_level,
            "escalated_at": now.isoformat(),
            "escalation_reason": "Complaint exceeded its assigned SLA.",
            # Optionally, we could store previous_assigned_officer here if status changes,
            # but per requirement we keep the officer and just mark escalated.
            "previous_assigned_officer": complaint_data.get("assigned_officer")
        }

    async def check_and_update_sla_for_complaint(self, complaint_id: str) -> Dict[str, Any]:
        """
        Fetch a complaint, calculate SLA status, update if needed, and return update dict.
        Returns a dict with the fields that were changed (or empty if no change).
        """
        try:
            complaint_ref = self.db.collection(self.complaints_collection).document(complaint_id)
            complaint_doc = complaint_ref.get()
            if not complaint_doc.exists:
                logger.warning(f"Complaint {complaint_id} not found")
                return {}

            data = complaint_doc.to_dict()
            sla_info = self.calculate_sla_status(data)

            # Determine if we need to update anything
            update_fields = {}
            changed = False

            # Check sla_status
            if data.get("sla_status") != sla_info["sla_status"]:
                update_fields["sla_status"] = sla_info["sla_status"]
                changed = True

            # Check escalation fields
            if data.get("escalated") != sla_info["escalated"]:
                update_fields["escalated"] = sla_info["escalated"]
                changed = True
            if data.get("escalation_level") != sla_info["escalation_level"]:
                update_fields["escalation_level"] = sla_info["escalation_level"]
                changed = True
            if data.get("escalation_reason") != sla_info["escalation_reason"]:
                update_fields["escalation_reason"] = sla_info["escalation_reason"]
                changed = True
            if data.get("escalated_at") != sla_info["escalated_at"]:
                update_fields["escalated_at"] = sla_info["escalated_at"]
                changed = True
            # previous_assigned_officer: we only set on escalation, but we can update if changed
            if data.get("previous_assigned_officer") != sla_info["previous_assigned_officer"]:
                update_fields["previous_assigned_officer"] = sla_info["previous_assigned_officer"]
                changed = True

            # If OVERDUE and not yet escaled, we need to escalate
            if sla_info["sla_status"] == "OVERDUE" and not data.get("escalated", False):
                escalation_update = self.escalate_complaint(data)
                for key, value in escalation_update.items():
                    if data.get(key) != value:
                        update_fields[key] = value
                        changed = True

            if changed:
                # Also update updated_at
                update_fields["updated_at"] = datetime.utcnow().isoformat()
                complaint_ref.update(update_fields)
                logger.info(f"Updated SLA/status for complaint {complaint_id}: {update_fields}")

            return update_fields

        except Exception as e:
            logger.error(f"Error checking SLA for complaint {complaint_id}: {str(e)}")
            return {}

    async def run_sla_check_all(self) -> Dict[str, int]:
        """
        Iterate over all complaints (not resolved) and update SLA status and escalation as needed.
        Returns counts.
        """
        try:
            complaints_ref = self.db.collection(self.complaints_collection)
            # We could filter by status not RESOLVED, but for simplicity we get all and skip resolved inside
            # For MVP, we'll stream all; in production you might want to index.
            checked = 0
            on_track = 0
            due_soon = 0
            overdue = 0
            resolved = 0
            newly_escalated = 0

            for doc in complaints_ref.stream():
                checked += 1
                data = doc.to_dict()
                complaint_id = doc.id

                # Skip if we want to only check unresolved? We'll still process resolved to keep sla_status RESOLVED
                sla_info = self.calculate_sla_status(data)

                # Count based on calculated sla_info (before potential escalation update)
                if sla_info["sla_status"] == "RESOLVED":
                    resolved += 1
                elif sla_info["sla_status"] == "ON_TRACK":
                    on_track += 1
                elif sla_info["sla_status"] == "DUE_SOON":
                    due_soon += 1
                elif sla_info["sla_status"] == "OVERDUE":
                    overdue += 1

                # Determine if we need to update (including escalation)
                update_fields = {}
                changed = False

                # sla_status
                if data.get("sla_status") != sla_info["sla_status"]:
                    update_fields["sla_status"] = sla_info["sla_status"]
                    changed = True

                # escalation fields
                if data.get("escalated") != sla_info["escalated"]:
                    update_fields["escalated"] = sla_info["escalated"]
                    changed = True
                if data.get("escalation_level") != sla_info["escalation_level"]:
                    update_fields["escalation_level"] = sla_info["escalation_level"]
                    changed = True
                if data.get("escalation_reason") != sla_info["escalation_reason"]:
                    update_fields["escalation_reason"] = sla_info["escalation_reason"]
                    changed = True
                if data.get("escalated_at") != sla_info["escalated_at"]:
                    update_fields["escalated_at"] = sla_info["escalated_at"]
                    changed = True
                if data.get("previous_assigned_officer") != sla_info["previous_assigned_officer"]:
                    update_fields["previous_assigned_officer"] = sla_info["previous_assigned_officer"]
                    changed = True

                # If OVERDUE and not escalated, escalate
                if sla_info["sla_status"] == "OVERDUE" and not data.get("escalated", False):
                    escalation_update = self.escalate_complaint(data)
                    for key, value in escalation_update.items():
                        if data.get(key) != value:
                            update_fields[key] = value
                            changed = True
                    # If we escalated, count as newly escalated
                    newly_escalated += 1

                if changed:
                    update_fields["updated_at"] = datetime.utcnow().isoformat()
                    doc.reference.update(update_fields)

            return {
                "checked": checked,
                "on_track": on_track,
                "due_soon": due_soon,
                "overdue": overdue,
                "resolved": resolved,
                "newly_escalated": newly_escalated
            }

        except Exception as e:
            logger.error(f"Error running SLA check all: {str(e)}")
            return {
                "checked": 0,
                "on_track": 0,
                "due_soon": 0,
                "overdue": 0,
                "resolved": 0,
                "newly_escalated": 0
            }

# Create a singleton instance
sla_service = SLAService()