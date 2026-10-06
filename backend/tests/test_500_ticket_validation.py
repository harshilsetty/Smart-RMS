"""
500+ Synthetic Ticket Validation & Performance Sanity Check (Section 31 & 32).
Validates schema compliance, relational integrity, SLA calculations, and measures local execution latency.
"""

import json
import time
from pathlib import Path
from app.config import settings
from app.schemas.contracts import RMSRequest
from app.integrations.mock_rms_adapter import MockRMSAdapter

def test_500_synthetic_tickets_schema_and_integrity():
    dataset_path = settings.MOCK_DATA_DIR / "generated_rms_requests.json"
    assert dataset_path.exists(), "Generated synthetic dataset must exist"

    with open(dataset_path, "r", encoding="utf-8") as f:
        records = json.load(f)

    # 1. Verify count
    assert len(records) >= 500, f"Expected at least 500 records, got {len(records)}"

    # 2. Load valid departments and users for relational reference checking
    with open(settings.MOCK_DATA_DIR / "departments.json", "r", encoding="utf-8") as f:
        depts = json.load(f)
    valid_dept_ids = {d.get("department_id") or d.get("id") for d in depts}
    valid_dept_names = {d["name"] for d in depts}

    with open(settings.MOCK_DATA_DIR / "users.json", "r", encoding="utf-8") as f:
        users = json.load(f)
    valid_user_ids = {u["user_id"] for u in users}

    valid_priorities = {"Low", "Medium", "High", "Critical"}
    valid_statuses = {
        "INGESTED", "ANALYZED", "ROUTED", "STAFF_REVIEW", "IN_PROGRESS",
        "WAITING_FOR_STUDENT", "WAITING_FOR_DEPARTMENT", "ESCALATED", "APPROVED", "RESOLVED", "CLOSED"
    }

    # 3. Validate every record against Pydantic RMSRequest schema and relational integrity
    for r in records:
        # Schema conformity validation
        parsed = RMSRequest(**r)
        assert parsed.ticket_id.startswith("TKT-SYN-")
        assert parsed.student_reference.startswith("STU-SYN-")
        assert parsed.is_synthetic is True

        # Reference integrity
        assert r["department"] in valid_dept_names, f"Unknown department: {r['department']}"
        assert r["assigned_department_id"] in valid_dept_ids, f"Unknown dept ID: {r['assigned_department_id']}"
        assert r["assigned_staff_id"] in valid_user_ids, f"Unknown staff ID: {r['assigned_staff_id']}"

        # Status & Priority integrity
        assert r["priority"] in valid_priorities
        assert r["status"] in valid_statuses

        # SLA record integrity
        sla = r["sla_record"]
        assert sla["sla_hours"] in [2, 4, 6, 8, 12, 18, 24, 36, 48, 72, 96]
        assert sla["status"] in ["ON_TRACK", "AT_RISK", "BREACHED", "RESOLVED"]

        # Timestamp integrity
        assert "T" in r["created_at"]
        assert "T" in r["due_at"]

        # No real PII patterns
        desc = r["description"].lower()
        assert "@gmail.com" not in desc
        assert "@yahoo.com" not in desc


def test_performance_sanity_check_against_500_records():
    """Measures local retrieval and analytics latency over 500 records."""
    adapter = MockRMSAdapter(data_file=settings.MOCK_DATA_DIR / "generated_rms_requests.json")

    # 1. Measure List Retrieval
    t0 = time.perf_counter()
    all_tickets = adapter.fetch_tickets()
    t_list = (time.perf_counter() - t0) * 1000.0  # ms
    assert len(all_tickets) >= 500

    # 2. Measure Filtered Search
    t0 = time.perf_counter()
    filtered = adapter.fetch_tickets(department="Hostel Affairs", priority="High")
    t_filter = (time.perf_counter() - t0) * 1000.0  # ms
    assert len(filtered) > 0

    # 3. Measure Single Ticket Retrieval
    first_id = all_tickets[0]["ticket_id"]
    t0 = time.perf_counter()
    single = adapter.get_ticket_by_id(first_id)
    t_single = (time.perf_counter() - t0) * 1000.0  # ms
    assert single is not None

    # 4. Measure History Retrieval
    t0 = time.perf_counter()
    history = adapter.get_audit_history(first_id)
    t_hist = (time.perf_counter() - t0) * 1000.0  # ms
    assert isinstance(history, list)

    # 5. Measure Operations Analytics Computation across 500 records
    t0 = time.perf_counter()
    analytics = adapter.get_operations_analytics()
    t_analytics = (time.perf_counter() - t0) * 1000.0  # ms
    assert analytics["total_tickets"] >= 500

    print("\n--- Local Performance Measurements (500 Records) ---")
    print(f"List All Tickets (500 items): {t_list:.2f} ms")
    print(f"Filtered Search:              {t_filter:.2f} ms")
    print(f"Single Ticket Detail:         {t_single:.2f} ms")
    print(f"Audit History Fetch:          {t_hist:.2f} ms")
    print(f"Full Analytics Computation:   {t_analytics:.2f} ms")

    # Sanity thresholds for local in-memory/JSON operations (sub-100ms)
    assert t_list < 150.0, f"List retrieval too slow: {t_list:.2f}ms"
    assert t_single < 20.0, f"Single ticket fetch too slow: {t_single:.2f}ms"
    assert t_analytics < 150.0, f"Analytics calculation too slow: {t_analytics:.2f}ms"
