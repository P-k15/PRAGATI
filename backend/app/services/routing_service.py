from typing import Optional, List, Dict, Any
from app.core.firebase import db
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class RoutingService:
    def __init__(self):
        self.db = db
        self.officers_collection = "officers"
        self.complaints_collection = "complaints"

    async def get_officers_by_department(self, department: str) -> List[Dict[str, Any]]:
        """
        Get all officers belonging to a specific department.
        """
        try:
            officers_ref = self.db.collection(self.officers_collection)
            officers_query = officers_ref.where("department", "==", department).where("available", "==", True)
            officers = []

            for doc in officers_query.stream():
                officer_data = doc.to_dict()
                officer_data["id"] = doc.id
                officers.append(officer_data)

            return officers
        except Exception as e:
            logger.error(f"Error fetching officers for department {department}: {str(e)}")
            return []

    async def get_active_complaint_count(self, officer_id: str) -> int:
        """
        Get the number of active complaints for an officer.
        Active complaints are those with status ASSIGNED or IN_PROGRESS.
        """
        try:
            complaints_ref = self.db.collection(self.complaints_collection)
            complaints_query = complaints_ref.where("assigned_officer", "==", officer_id)\
                .where("status", "in", ["ASSIGNED", "IN_PROGRESS"])

            count = 0
            for _ in complaints_query.stream():
                count += 1

            return count
        except Exception as e:
            logger.error(f"Error counting active complaints for officer {officer_id}: {str(e)}")
            return 0

    async def select_officer(self, department: str, complaint_id: str) -> Optional[Dict[str, Any]]:
        """
        Select the best officer for a complaint based on department and workload.

        Algorithm:
        1. Find officers belonging to the AI-selected department.
        2. Consider only officers where available == true.
        3. Prefer the officer with the fewest active complaints.
        4. If multiple officers have the same active complaint count, use officer ID as tie-breaker.
        5. If no eligible officer exists, return None.
        """
        try:
            # Get available officers in the department
            officers = await self.get_officers_by_department(department)

            if not officers:
                logger.warning(f"No available officers found for department: {department}")
                return None

            # For each officer, get active complaint count
            officer_workloads = []
            for officer in officers:
                active_count = await self.get_active_complaint_count(officer["id"])
                officer_workloads.append({
                    "officer": officer,
                    "active_complaints": active_count
                })

            # Sort by active complaints (ascending), then by officer ID (ascending) for deterministic tie-breaking
            officer_workloads.sort(key=lambda x: (x["active_complaints"], x["officer"]["id"]))

            # Select the officer with the least workload
            selected = officer_workloads[0]

            logger.info(f"Selected officer {selected['officer']['id']} for department {department} "
                       f"with {selected['active_complaints']} active complaints")

            return selected["officer"]

        except Exception as e:
            logger.error(f"Error selecting officer for department {department}: {str(e)}")
            return None

    async def update_officer_workload(self, officer_id: str, increment: bool = True) -> bool:
        """
        Update the active_complaints count for an officer.
        If increment=True, increase count; if False, decrease count.
        """
        try:
            officer_ref = self.db.collection(self.officers_collection).document(officer_id)
            officer_doc = officer_ref.get()

            if not officer_doc.exists:
                logger.error(f"Officer {officer_id} not found")
                return False

            current_data = officer_doc.to_dict()
            current_count = current_data.get("active_complaints", 0)

            if increment:
                new_count = current_count + 1
            else:
                new_count = max(0, current_count - 1)  # Ensure we don't go below 0

            officer_ref.update({"active_complaints": new_count})
            logger.info(f"Updated officer {officer_id} active_complaints from {current_count} to {new_count}")
            return True

        except Exception as e:
            logger.error(f"Error updating workload for officer {officer_id}: {str(e)}")
            return False

    async def assign_complaint_to_officer(self, complaint_id: str, officer_id: str) -> bool:
        """
        Assign a complaint to an officer and update routing metadata.
        """
        try:
            complaint_ref = self.db.collection(self.complaints_collection).document(complaint_id)

            update_data = {
                "assigned_officer": officer_id,
                "status": "ASSIGNED",
                "assigned_at": datetime.utcnow().isoformat(),
                "routing_source": "rule_based",
                "routing_reason": f"Assigned to available officer with lowest active workload.",
                "updated_at": datetime.utcnow().isoformat()
            }

            complaint_ref.update(update_data)

            # Update officer's active complaint count
            await self.update_officer_workload(officer_id, increment=True)

            logger.info(f"Complaint {complaint_id} assigned to officer {officer_id}")
            return True

        except Exception as e:
            logger.error(f"Error assigning complaint {complaint_id} to officer {officer_id}: {str(e)}")
            return False

# Create a singleton instance
routing_service = RoutingService()