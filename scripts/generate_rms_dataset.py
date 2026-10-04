import argparse
import json
import random
from pathlib import Path
from typing import List, Dict, Any

TEMPLATES = [
    # HOSTEL_MAINTENANCE
    {
        "intent": "HOSTEL_MAINTENANCE",
        "department": "Hostel Affairs",
        "priority": "High",
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
        "priority": "High",
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
        "priority": "Critical",
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
        "priority": "Medium",
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
        "priority": "Medium",
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
        "entities": {"illness": ["typhoid", "dengue fever", "viral hepatitis", "acute gastroenteritis"]}
    },
    # SCHOLARSHIP
    {
        "intent": "SCHOLARSHIP",
        "department": "Scholarship Section",
        "priority": "High",
        "subject_templates": [
            "National Scholarship Portal NSP verification pending at institute level",
            "Post-Matric PMS scholarship renewal portal verification delay",
            "State scholarship application pending verification nearing closing date",
            "Merit scholarship fee concession adjustment in term invoice",
            "Central Sector Scheme scholarship institutional endorsement status"
        ],
        "desc_templates": [
            "Dear Scholarship Section, my application on National Scholarship Portal (NSP) is pending institute-level verification. The state portal closes on 30th September. Please verify application ID: NSP-2026-{reg}.",
            "My Post-Matric scholarship renewal has been awaiting Nodal Officer verification for over 3 weeks. Aadhaar authentication is completed. Kindly approve before deadline.",
            "I qualified for university merit scholarship with 9.2 CGPA. Please adjust the fee concession of INR {amount} in my current semester ledger."
        ],
        "entities": {}
    },
    # IT_SUPPORT
    {
        "intent": "IT_SUPPORT",
        "department": "IT Services",
        "priority": "Low",
        "subject_templates": [
            "Campus Wi-Fi Fortinet MAC address registration error (2/2 limit)",
            "Student UMS credentials locked and password reset link not received",
            "Student email mailbox storage quota full and bouncing emails",
            "Wi-Fi access point offline in {hostel_block} corridor",
            "Laboratory computer workstation domain authentication login error"
        ],
        "desc_templates": [
            "IT Helpdesk, trying to register new MAC address {mac} on Fortinet Wi-Fi registration portal. It reports device limit reached although old device was deleted. Student phone: +91-{phone}.",
            "My student UMS login is locked after multiple invalid password attempts. Password reset link is not reaching my personal email. Contact: {email}.",
            "The wireless access point in {hostel_block} has been offline all day. Students are unable to connect to campus internet network."
        ],
        "entities": {}
    },
    # STUDENT_SERVICES
    {
        "intent": "STUDENT_SERVICES",
        "department": "Academic Affairs",
        "priority": "Low",
        "subject_templates": [
            "Request for official Bonafide Certificate and MOI letter for visa",
            "Bonafide certificate required for educational bank loan renewal",
            "Medium of Instruction verification certificate for foreign university",
            "Duplicate student identity card issuance request",
            "Migration certificate dispatch tracking status inquiry"
        ],
        "desc_templates": [
            "Respected Registrar Office, I require an official stamped Bonafide Certificate and English Medium of Instruction (MOI) verification letter for embassy visa application. All dues cleared.",
            "Applying for bank education loan renewal at {bank}. Kindly issue digitally signed Bonafide Student Certificate stating current semester {sem} enrollment.",
            "I paid the fee for duplicate student ID card yesterday after losing my card on campus. Please inform collection desk details."
        ],
        "entities": {}
    }
]

HOSTEL_BLOCKS = ["BH-1", "BH-2", "BH-3", "BH-4", "BH-5", "BH-6", "BH-7", "BH-8", "GH-1", "GH-2", "GH-3", "GH-4"]
COURSES = ["CSE 472", "CSE 320", "MTH 402", "INT 108", "ECE 213", "MGT 101", "PEA 305", "CSE 202"]
BANKS = ["HDFC Bank", "SBI", "ICICI Bank", "Punjab National Bank", "Axis Bank"]
DATES = ["12th Sept", "15th Sept", "18th Sept", "20th Sept", "22nd Sept", "25th Sept", "28th Sept", "30th Sept"]

def generate_synthetic_dataset(count: int = 500, seed: int = 42) -> List[Dict[str, Any]]:
    random.seed(seed)
    dataset: List[Dict[str, Any]] = []

    for i in range(count):
        cat = random.choice(TEMPLATES)
        ticket_id = f"TKT-SYN-{2000 + i + 1}"
        student_ref = f"STU-SYN-{random.randint(1000, 9999)}"
        hostel = random.choice(HOSTEL_BLOCKS)
        room = f"{random.randint(1, 6)}{random.randint(0, 9):02d}"
        course = random.choice(COURSES)
        bank = random.choice(BANKS)
        date = random.choice(DATES)
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

        # Critical hazard or deadline adjustments
        priority = cat["priority"]
        if "switchboard" in desc.lower() or "power" in desc.lower() or "24 hours" in desc.lower():
            priority = "Critical"

        dataset.append({
            "ticket_id": ticket_id,
            "student_reference": student_ref,
            "subject": subject,
            "description": desc,
            "ground_truth_intent": cat["intent"],
            "ground_truth_department": cat["department"],
            "ground_truth_priority": priority,
            "created_at": "2026-09-21T12:00:00Z"
        })

    return dataset

def main():
    parser = argparse.ArgumentParser(description="Generate synthetic RMS dataset for scale load simulation and testing.")
    parser.add_argument("--count", type=int, default=500, help="Number of synthetic records to generate (default: 500)")
    parser.add_argument("--seed", type=int, default=42, help="Random generator seed for determinism (default: 42)")
    parser.add_argument("--output", type=str, default="data/mock/generated_rms_requests.json", help="Destination file path")

    args = parser.parse_args()

    # Determine absolute path
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
