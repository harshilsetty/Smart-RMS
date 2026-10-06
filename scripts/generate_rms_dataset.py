import argparse
import json
import random
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime, timezone, timedelta

TEMPLATES = [
    # HOSTEL_MAINTENANCE
    {
        "intent": "HOSTEL_MAINTENANCE",
        "department": "Hostel Affairs",
        "dept_id": "DEPT-HOSTEL",
        "staff_id": "USR-STAFF-01",
        "category": "Hostel",
        "priority": "High",
        "sla_hours": {"LOW": 48, "MEDIUM": 24, "HIGH": 12, "CRITICAL": 4},
        "subject_templates": [
            "Water leakage in {hostel_block} Room {room_number}",
            "AC unit malfunctioning and noisy in {hostel_block}",
            "Broken window latch and cold draft in Room {room_number}",
            "Geyser power tripping in {hostel_block} washroom",
            "Corridor ceiling water seepage near electrical board in {hostel_block}"
        ],
        "desc_templates": [
            "Respected Warden, in {hostel_block} Room {room_number}, the {fixture} has been leaking continuously since yesterday. Please send maintenance technician. Contact: +91-{phone}.",
            "The split AC unit in Room {room_number} of {hostel_block} stopped working and makes a loud rattling sound. Please inspect as soon as possible. Student ID: REG-2024-{reg}.",
            "Water is dripping from the bathroom pipe near the electrical point in {hostel_block} Room {room_number}. Need urgent repair. Phone: {phone}."
        ],
        "entities": {"fixture": ["washbasin tap", "AC drainage line", "ceiling pipe", "shower fitting"]}
    },
    # FEE_PAYMENT
    {
        "intent": "FEE_PAYMENT",
        "department": "Accounts & Finance",
        "dept_id": "DEPT-ACCOUNTS",
        "staff_id": "USR-STAFF-03",
        "category": "Finance",
        "priority": "High",
        "sla_hours": {"LOW": 72, "MEDIUM": 48, "HIGH": 24, "CRITICAL": 12},
        "subject_templates": [
            "Semester {sem} fee debited twice from {bank} account",
            "Tuition fee deduction timeout during online payment",
            "Excess fee adjustment request for Term {sem}",
            "Online payment gateway timed out but INR {amount} deducted",
            "Duplicate transaction reference {txn_id} fee refund"
        ],
        "desc_templates": [
            "Dear Accounts Team, while paying my Semester {sem} tuition fee of INR {amount} through {bank} on {date}, the payment timed out. However amount was debited twice. Transaction ID: TXN-{txn_id}. Please reconcile and refund to {email}.",
            "My bank statement indicates double deduction for semester registration. Only one payment is credited in fee ledger. Please initiate refund for duplicate transaction TXN-{txn_id}.",
            "Paid hostel fee of INR {amount} via online portal using {bank}. Transaction was successful at bank end but receipt not generated. Kindly update portal ledger."
        ],
        "entities": {}
    },
    # EXAMINATION
    {
        "intent": "EXAMINATION",
        "department": "Examination Branch",
        "dept_id": "DEPT-EXAM",
        "staff_id": "USR-STAFF-04",
        "category": "Examination",
        "priority": "Critical",
        "sla_hours": {"LOW": 48, "MEDIUM": 24, "HIGH": 12, "CRITICAL": 4},
        "subject_templates": [
            "Admit card blocked due to clearance error before exam",
            "Hall ticket download failure with exam in {hours} hours",
            "Library clearance hold blocking examination hall ticket",
            "End Term Exam datesheet clash for {course_code}",
            "Emergency admit card override request for scheduled exam"
        ],
        "desc_templates": [
            "Controller of Examinations, my end-term exam commences in {hours} hours. The student portal says 'Admit Card Blocked - Pending Library Clearance', but I have already returned books and hold counter receipt. Please release admit card.",
            "Urgent: Unable to download hall ticket for exam scheduled tomorrow. All dues and laboratory clearances are cleared. Registration: 1220{reg}.",
            "My examination datesheet shows two papers ({course_code} and MTH 402) scheduled on the exact same date and morning slot. Kindly rectify the timetable clash."
        ],
        "entities": {}
    },
    # ACADEMIC
    {
        "intent": "ACADEMIC",
        "department": "Academic Affairs",
        "dept_id": "DEPT-ACADEMICS",
        "staff_id": "USR-STAFF-02",
        "category": "Academics",
        "priority": "Medium",
        "sla_hours": {"LOW": 72, "MEDIUM": 48, "HIGH": 24, "CRITICAL": 8},
        "subject_templates": [
            "Continuous Assessment CA-2 marks discrepancy in {course_code}",
            "CA rubric evaluation score not reflecting in portal ledger",
            "Marks missing for assignment submission in {course_code}",
            "Elective course registration allocation error for Term {sem}",
            "Syllabus out-of-scope question in midterm examination"
        ],
        "desc_templates": [
            "Respected Dean of Academics, for course {course_code}, my evaluated rubric score was 27/30 as confirmed by teacher remarks, but portal displays 12/30. Attached evaluator marksheet screenshot.",
            "In continuous assessment for {course_code}, my CA-3 assignment is marked Absent although submitted on LMS before due date. Registration: REG-2023-{reg}.",
            "During course selection, {course_code} was allotted instead of my chosen elective. Please adjust my credit registration ledger."
        ],
        "entities": {}
    },
    # ATTENDANCE
    {
        "intent": "ATTENDANCE",
        "department": "Student Welfare",
        "dept_id": "DEPT-WELFARE",
        "staff_id": "USR-STAFF-05",
        "category": "Student Welfare",
        "priority": "Medium",
        "sla_hours": {"LOW": 72, "MEDIUM": 36, "HIGH": 18, "CRITICAL": 6},
        "subject_templates": [
            "Medical leave attendance condonation for hospitalization period",
            "Attendance adjustment for dengue fever recovery",
            "Duty leave attendance credit for inter-university sports meet",
            "Biometric punch machine sync failure in Block {block}",
            "Health center endorsed medical certificate attendance duty"
        ],
        "desc_templates": [
            "Head of Student Welfare, I was admitted to hospital due to acute {illness} from {date}. My attendance in {course_code} dropped to 71%. Submitting certified discharge summary and fitness certificate for attendance condonation.",
            "Requesting attendance duty adjustment for 6 days absence due to hospitalization. Medical certificates have been verified at University Health Center.",
            "Biometric attendance device in Block {block} Room 201 failed to register morning class punches. Requesting attendance duty credit."
        ],
        "entities": {"illness": ["dengue fever", "typhoid", "severe viral illness", "fracture rehabilitation"]}
    },
    # SCHOLARSHIP
    {
        "intent": "SCHOLARSHIP",
        "department": "Scholarship Section",
        "dept_id": "DEPT-SCHOLARSHIP",
        "staff_id": "USR-STAFF-06",
        "category": "Scholarship",
        "priority": "High",
        "sla_hours": {"LOW": 96, "MEDIUM": 72, "HIGH": 36, "CRITICAL": 12},
        "subject_templates": [
            "National Scholarship Portal institutional verification pending",
            "Post-Matric scholarship state nodal officer approval delay",
            "Merit-based university scholarship disbursement inquiry",
            "Aadhaar linkage mismatch on state welfare scholarship portal",
            "Income certificate verification hold for scholarship renewal"
        ],
        "desc_templates": [
            "Dear Nodal Officer, my NSP 2026 application verification is pending at the institute level. Portal closing date is approaching. Please verify my student record so state welfare department can release funds.",
            "My scholarship disbursement of INR {amount} has been approved by government but institutional verification status is unverified. Registration: 1220{reg}.",
            "Submitted renewal documents for merit scholarship 2 weeks ago. Please update verification status on student UMS dashboard."
        ],
        "entities": {}
    },
    # IT_SERVICES
    {
        "intent": "IT_SERVICES",
        "department": "IT Services",
        "dept_id": "DEPT-IT",
        "staff_id": "USR-STAFF-07",
        "category": "IT Services",
        "priority": "Low",
        "sla_hours": {"LOW": 48, "MEDIUM": 24, "HIGH": 8, "CRITICAL": 2},
        "subject_templates": [
            "Campus Wi-Fi MAC address registration limit error",
            "University email account password reset request",
            "Student portal LMS login authentication failure",
            "Laboratory desktop network drive inaccessible in Block {block}",
            "Fortinet firewall captive portal connection timeout"
        ],
        "desc_templates": [
            "IT Helpdesk, replaced my phone and unable to register new MAC address {mac} on university Wi-Fi portal. Error shows device limit exceeded. Please unbind old device.",
            "Cannot log in to student portal after password expiration. Need authentication reset link sent to registered mobile.",
            "Campus Wi-Fi disconnects continuously in Block {block} lecture hall. Signal strength drops to zero during class hours."
        ],
        "entities": {}
    }
]

HOSTELS = ["BH-1", "BH-2", "BH-3", "BH-4", "BH-5", "GH-1", "GH-2", "GH-3"]
BANKS = ["HDFC Bank", "State Bank of India", "ICICI Bank", "Punjab National Bank", "Axis Bank"]
COURSES = ["CSE 472", "CSE 320", "INT 213", "MTH 402", "ECE 216", "CSE 316"]
LIFECYCLE_STATES = [
    "INGESTED",
    "ANALYZED",
    "ROUTED",
    "STAFF_REVIEW",
    "IN_PROGRESS",
    "WAITING_FOR_STUDENT",
    "WAITING_FOR_DEPARTMENT",
    "ESCALATED",
    "APPROVED",
    "RESOLVED",
    "CLOSED"
]

def generate_synthetic_dataset(count: int = 500, seed: int = 42) -> List[Dict[str, Any]]:
    random.seed(seed)
    dataset: List[Dict[str, Any]] = []

    base_time = datetime(2026, 9, 21, 10, 0, 0, tzinfo=timezone.utc)

    for i in range(1, count + 1):
        cat = random.choice(TEMPLATES)
        ticket_id = f"TKT-SYN-{2000 + i}"
        student_ref = f"STU-SYN-{random.randint(1000, 9999)}"

        hostel = random.choice(HOSTELS)
        room = str(random.randint(101, 520))
        course = random.choice(COURSES)
        bank = random.choice(BANKS)
        date = f"{random.randint(10, 22)}th Sept 2026"
        amount = f"{random.randint(20, 85)},000"
        sem = str(random.randint(1, 8))
        phone = f"98{random.randint(10000000, 99999999)}"
        reg = f"{random.randint(1000, 9999)}"
        txn = f"{random.randint(10000000, 99999999)}"
        email = f"student.{random.randint(100, 999)}@lpu.in"
        mac = f"00:1A:2B:{random.randint(10,99)}:{random.randint(10,99)}:{random.randint(10,99)}"
        hours = str(random.choice([24, 36, 48]))
        block = str(random.randint(30, 38))

        subject_template = random.choice(cat["subject_templates"])
        desc_template = random.choice(cat["desc_templates"])

        format_args = {
            "hostel_block": hostel,
            "room_number": room,
            "course_code": course,
            "bank": bank,
            "date": date,
            "amount": amount,
            "sem": sem,
            "phone": phone,
            "reg": reg,
            "txn_id": txn,
            "email": email,
            "mac": mac,
            "hours": hours,
            "block": block,
            "fixture": random.choice(cat["entities"].get("fixture", ["fixture"])),
            "illness": random.choice(cat["entities"].get("illness", ["dengue fever"]))
        }

        subject = subject_template.format(**format_args)
        desc = desc_template.format(**format_args)

        # Critical hazard adjustments
        priority = cat["priority"]
        if "switchboard" in desc.lower() or "power" in desc.lower() or "24 hours" in desc.lower():
            priority = "Critical"

        # Realistic lifecycle distribution
        status = random.choice(LIFECYCLE_STATES)
        escalation_level = 1 if status == "ESCALATED" else 0

        # Timestamp generation
        offset_hours = random.randint(1, 120)
        ticket_time = base_time - timedelta(hours=offset_hours)
        ticket_time_iso = ticket_time.isoformat()

        # Compute SLA
        sla_hours = cat["sla_hours"].get(priority.upper(), 48)
        due_time = ticket_time + timedelta(hours=sla_hours)
        due_time_iso = due_time.isoformat()

        # Deterministic SLA status calculation
        rem_sec = (due_time - base_time).total_seconds()
        rem_hrs = round(rem_sec / 3600.0, 1)

        if status in ["RESOLVED", "APPROVED", "CLOSED"]:
            sla_st = "RESOLVED"
            is_breached = False
        elif rem_sec <= 0:
            sla_st = "BREACHED"
            is_breached = True
        elif rem_hrs <= max(sla_hours * 0.25, 4.0):
            sla_st = "AT_RISK"
            is_breached = False
        else:
            sla_st = "ON_TRACK"
            is_breached = False

        record = {
            "ticket_id": ticket_id,
            "external_reference": f"UMS-EXT-{2000 + i}",
            "student_reference": student_ref,
            "title": subject,
            "subject": subject,
            "description": desc,
            "redacted_description": desc,
            "category": cat["category"],
            "subcategory": cat["intent"],
            "department": cat["department"],
            "assigned_department_id": cat["dept_id"],
            "assigned_staff_id": cat["staff_id"],
            "assigned_staff": cat["staff_id"],
            "priority": priority,
            "status": status,
            "escalation_level": escalation_level,
            "source": "STUDENT_PORTAL",
            "created_at": ticket_time_iso,
            "updated_at": ticket_time_iso,
            "due_at": due_time_iso,
            "tags": [cat["category"].lower(), priority.lower(), status.lower()],
            "attachments": [],
            "responses": [
                {
                    "response_id": f"RSP-{2000 + i}-01",
                    "ticket_id": ticket_id,
                    "author_id": cat["staff_id"],
                    "author_name": "University Staff",
                    "author_role": "STAFF_OPERATOR",
                    "response_type": "STAFF",
                    "status": "PUBLISHED",
                    "content": f"Ticket logged and queued for {cat['department']} review.",
                    "is_internal": True,
                    "created_at": ticket_time_iso
                }
            ],
            "assignments": [
                {
                    "assignment_id": f"ASG-{2000 + i}-01",
                    "ticket_id": ticket_id,
                    "department_id": cat["dept_id"],
                    "staff_id": cat["staff_id"],
                    "assigned_by": "SYSTEM",
                    "assigned_at": ticket_time_iso,
                    "reason": "Initial operational routing",
                    "active": True
                }
            ],
            "escalations": [
                {
                    "escalation_id": f"ESC-{2000 + i}-01",
                    "ticket_id": ticket_id,
                    "escalated_by": cat["staff_id"],
                    "target_role": "DEPARTMENT_HOD",
                    "previous_level": "LEVEL_0",
                    "new_level": "LEVEL_1",
                    "reason": "SLA warning or complexity escalation",
                    "urgent": False,
                    "escalated_at": ticket_time_iso,
                    "status": "PENDING"
                }
            ] if escalation_level > 0 else [],
            "history": [
                {
                    "event_id": f"AUD-{2000 + i}-01",
                    "ticket_id": ticket_id,
                    "event_type": "INGESTED",
                    "actor_id": student_ref,
                    "actor_role": "STUDENT",
                    "timestamp": ticket_time_iso,
                    "from_state": "NEW",
                    "to_state": "INGESTED",
                    "notes": "Ticket ingested via synthetic portal",
                    "details": {"source": "STUDENT_PORTAL"}
                }
            ],
            "sla_record": {
                "priority": priority,
                "sla_hours": sla_hours,
                "due_at": due_time_iso,
                "is_breached": is_breached,
                "remaining_hours": rem_hrs,
                "status": sla_st
            },
            "metadata": {"environment": "synthetic", "batch": "milestone_2"},
            "is_synthetic": True,
            # Ground truth fields for NLP benchmarks
            "ground_truth_intent": cat["intent"],
            "ground_truth_department": cat["department"],
            "ground_truth_priority": priority
        }

        # If resolved or closed, add resolution fields
        if status in ["RESOLVED", "CLOSED"]:
            resolved_time = ticket_time + timedelta(hours=random.randint(2, min(sla_hours, 24)))
            record["resolved_at"] = resolved_time.isoformat()
            record["resolution_text"] = f"Official resolution provided by {cat['department']} staff: action confirmed."
            record["resolving_actor"] = cat["staff_id"]
            if status == "CLOSED":
                closed_time = resolved_time + timedelta(hours=random.randint(1, 12))
                record["closed_at"] = closed_time.isoformat()
                record["closing_actor"] = cat["staff_id"]

        dataset.append(record)

    return dataset

def main():
    parser = argparse.ArgumentParser(description="Generate synthetic RMS dataset for scale load simulation and testing.")
    parser.add_argument("--count", type=int, default=500, help="Number of synthetic records to generate (default: 500)")
    parser.add_argument("--seed", type=int, default=42, help="Random generator seed for determinism (default: 42)")
    parser.add_argument("--output", type=str, default="data/mock/generated_rms_requests.json", help="Destination file path")

    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    output_path = repo_root / args.output if not Path(args.output).is_absolute() else Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"[*] Generating {args.count} synthetic RMS records with seed={args.seed}...")
    dataset = generate_synthetic_dataset(count=args.count, seed=args.seed)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2)

    print(f"[+] Successfully generated {len(dataset)} records at: {output_path}")

if __name__ == "__main__":
    main()
