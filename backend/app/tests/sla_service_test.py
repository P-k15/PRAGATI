import sys
import os
from datetime import datetime, timezone, timedelta
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from services.sla_service import calculate_sla_status, is_overdue, should_escalate, escalate_complaint

def test_sla_service():
    print("Testing SLA Service...")

    # Create a base complaint for testing
    now = datetime.now(timezone.utc)
    base_complaint = {
        "id": "test_complaint_1",
        "citizen_id": "citizen_001",
        "description": "Test complaint",
        "location": "Test Location",
        "status": "ASSIGNED",
        "category": "Infrastructure",
        "sla_hours": 48,
        "sla_deadline": (now + timedelta(hours=48)).isoformat(),
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
        "assigned_officer": "officer_001",
        # SLA fields (will be calculated)
        "sla_status": None,
        "escalation_level": 0,
        "escalated": False,
        "escalated_at": None,
        "escalation_reason": None,
        "previous_assigned_officer": None
    }

    print("\n1. Testing ON_TRACK status (fresh complaint)")
    complaint = base_complaint.copy()
    status = calculate_sla_status(complaint)
    print(f"   SLA Status: {status}")
    assert status == "ON_TRACK", f"Expected ON_TRACK, got {status}"
    print("   PASS")

    print("\n2. Testing DUE_SOON status (25% of SLA remaining)")
    # Set deadline to be in the future, but within 25% of SLA time
    created = now - timedelta(hours=36)  # Created 36 hours ago
    deadline = created + timedelta(hours=48)  # 48 hour SLA
    current = deadline - timedelta(hours=12)  # 12 hours before deadline (25% of 48 = 12)

    complaint = base_complaint.copy()
    complaint["created_at"] = created.isoformat()
    complaint["sla_deadline"] = deadline.isoformat()
    complaint["updated_at"] = now.isoformat()

    status = calculate_sla_status(complaint, current)
    print(f"   SLA Status: {status}")
    print(f"   Created: {created.isoformat()}")
    print(f"   Deadline: {deadline.isoformat()}")
    print(f"   Current: {current.isoformat()}")
    assert status == "DUE_SOON", f"Expected DUE_SOON, got {status}"
    print("   PASS")

    print("\n3. Testing OVERDUE status (past deadline)")
    complaint = base_complaint.copy()
    # Set deadline to be in the past
    complaint["sla_deadline"] = (now - timedelta(hours=1)).isoformat()  # 1 hour ago
    status = calculate_sla_status(complaint)
    print(f"   SLA Status: {status}")
    assert status == "OVERDUE", f"Expected OVERDUE, got {status}"
    print("   PASS")

    print("\n4. Testing RESOLVED status overrides SLA")
    complaint = base_complaint.copy()
    complaint["status"] = "RESOLVED"
    # Even with past deadline, if resolved should be RESOLVED
    complaint["sla_deadline"] = (now - timedelta(hours=1)).isoformat()  # 1 hour ago
    status = calculate_sla_status(complaint)
    print(f"   SLA Status: {status}")
    assert status == "RESOLVED", f"Expected RESOLVED, got {status}"
    print("   PASS")

    print("\n5. Testing is_overdue function")
    complaint = base_complaint.copy()
    complaint["sla_deadline"] = (now - timedelta(hours=1)).isoformat()  # 1 hour ago
    overdue = is_overdue(complaint)
    print(f"   Is Overdue: {overdue}")
    assert overdue == True, f"Expected True, got {overdue}"
    print("   PASS")

    print("\n6. Testing should_escalate function")
    # Should escalate if overdue and not already escalated
    complaint = base_complaint.copy()
    complaint["sla_deadline"] = (now - timedelta(hours=1)).isoformat()  # 1 hour ago
    complaint["escalated"] = False
    should = should_escalate(complaint)
    print(f"   Should Escalate: {should}")
    assert should == True, f"Expected True, got {should}"

    # Should NOT escalate if already escalated
    complaint["escalated"] = True
    should = should_escalate(complaint)
    print(f"   Should Escalate (already escalated): {should}")
    assert should == False, f"Expected False, got {should}"
    print("   PASS")

    print("\n7. Testing escalate_complaint function")
    complaint = base_complaint.copy()
    complaint["sla_deadline"] = (now - timedelta(hours=1)).isoformat()  # 1 hour ago
    complaint["escalated"] = False
    complaint["escalation_level"] = 0

    escalated = escalate_complaint(complaint)
    print(f"   Escalated: {escalated['escalated']}")
    print(f"   Escalation Level: {escalated['escalation_level']}")
    print(f"   Escalation Reason: {escalated['escalation_reason']}")

    assert escalated["escalated"] == True, "Expected escalated to be True"
    assert escalated["escalation_level"] == 1, f"Expected escalation_level 1, got {escalated['escalation_level']}"
    assert escalated["escalation_reason"] == "Complaint exceeded its assigned SLA.", f"Unexpected escalation reason"
    assert escalated["previous_assigned_officer"] == "officer_001", f"Expected previous officer to be preserved"
    print("   PASS")

    print("\n8. Testing repeated escalation does not increase level")
    # Call escalate again - level should remain 1
    escalated2 = escalate_complaint(escalated)
    print(f"   Second Escalation Level: {escalated2['escalation_level']}")
    assert escalated2["escalation_level"] == 1, f"Expected escalation_level to remain 1, got {escalated2['escalation_level']}"
    print("   PASS")

    print("\nAll tests passed!")
    return True

if __name__ == "__main__":
    try:
        test_sla_service()
        print("\nSLA Service tests completed successfully!")
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)