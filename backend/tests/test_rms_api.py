from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_list_tickets():
    response = client.get("/api/v1/rms")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "tickets" in data
    assert data["total"] > 0

def test_list_tickets_with_filters():
    response = client.get("/api/v1/rms?department=Hostel Affairs")
    assert response.status_code == 200
    data = response.json()
    for t in data["tickets"]:
        assert t["department"] == "Hostel Affairs"

def test_get_ticket_detail():
    response = client.get("/api/v1/rms/TKT-RMS-1001")
    assert response.status_code == 200
    data = response.json()
    assert data["ticket_id"] == "TKT-RMS-1001"
    assert "redacted_description" in data

def test_analyze_ticket():
    response = client.post("/api/v1/rms/TKT-RMS-1001/analyze")
    assert response.status_code == 200
    data = response.json()
    assert data["ticket_id"] == "TKT-RMS-1001"
    assert "ai_analysis" in data
    assert "intent" in data["ai_analysis"]
    assert "confidence" in data["ai_analysis"]
    assert data["ai_analysis"]["confidence"] >= 0.7

def test_get_draft_response():
    response = client.get("/api/v1/rms/TKT-RMS-1001/draft")
    assert response.status_code == 200
    data = response.json()
    assert "draft_response" in data
    assert "sources" in data
    assert len(data["sources"]) > 0

def test_approve_ticket():
    payload = {
        "staff_id": "STAFF-902",
        "approved_text": "Maintenance electrician has been scheduled to inspect BH-4 Room 312.",
        "notes": "Verified against maintenance supervisor log."
    }
    response = client.post("/api/v1/rms/TKT-RMS-1001/approve", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "APPROVED"
    assert data["approved_by"] == "STAFF-902"

def test_escalate_ticket():
    payload = {
        "staff_id": "STAFF-902",
        "target_role": "DEPARTMENT_HOD",
        "reason": "Special approval required for appliance replacement."
    }
    response = client.post("/api/v1/rms/TKT-RMS-1002/escalate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ESCALATED"

def test_redirect_ticket():
    payload = {
        "staff_id": "STAFF-902",
        "new_department": "Accounts & Finance",
        "reason": "Misrouted by student; issue is refund related."
    }
    response = client.post("/api/v1/rms/TKT-RMS-1003/redirect", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["new_department"] == "Accounts & Finance"

def test_analytics_overview():
    response = client.get("/api/v1/analytics/overview")
    assert response.status_code == 200
    data = response.json()
    assert data["total_tickets"] > 0
    assert "ai_acceptance_rate" in data
