"""
Smart RMS - Milestone 6 Synthetic Grounding Evaluation Dataset Generator
Generates >= 150 authoritative claim-evidence pairs across 12 distinct variation categories:
1. Supported claims
2. Contradicted claims
3. Neutral claims
4. Paraphrases
5. Numeric changes
6. Deadline changes
7. Eligibility changes
8. Fee changes
9. Exception changes
10. Irrelevant evidence
11. Missing evidence
12. Ambiguous evidence
"""

import json
from pathlib import Path

DATASET_PATH = Path(__file__).resolve().parent.parent / "evaluation" / "datasets" / "claim_grounding_150.json"

RAW_CASES = [
    # -------------------------------------------------------------
    # 1. Supported Claims (Entailment)
    # -------------------------------------------------------------
    {
        "id": "SUP-01",
        "category": "DEADLINE",
        "variation": "supported",
        "evidence": "Students seeking end-term re-evaluation must submit their application within 7 calendar days of result declaration.",
        "claim": "Applications for end-term re-evaluation must be submitted within 7 calendar days.",
        "label": "ENTAILMENT",
        "is_high_impact": True
    },
    {
        "id": "SUP-02",
        "category": "FEE",
        "variation": "supported",
        "evidence": "The non-refundable re-evaluation processing fee is ₹500 per theory course.",
        "claim": "A non-refundable fee of ₹500 per theory course is required for re-evaluation.",
        "label": "ENTAILMENT",
        "is_high_impact": True
    },
    {
        "id": "SUP-03",
        "category": "ELIGIBILITY",
        "variation": "supported",
        "evidence": "Students must maintain a minimum attendance of 75% across all registered courses to appear for final examinations.",
        "claim": "A minimum of 75% attendance across all registered courses is mandatory to sit for final examinations.",
        "label": "ENTAILMENT",
        "is_high_impact": True
    },
    {
        "id": "SUP-04",
        "category": "PROCESS",
        "variation": "supported",
        "evidence": "Duplicate ID cards can be requested via the University Student Portal under the Student Services section.",
        "claim": "Students can apply for duplicate ID cards through the University Student Portal under Student Services.",
        "label": "ENTAILMENT",
        "is_high_impact": False
    },
    {
        "id": "SUP-05",
        "category": "FEE",
        "variation": "supported",
        "evidence": "A replacement charge of ₹200 applies for reissuing a lost student RFID card.",
        "claim": "Reissuing a lost RFID card incurs a replacement charge of ₹200.",
        "label": "ENTAILMENT",
        "is_high_impact": True
    },
    {
        "id": "SUP-06",
        "category": "DEADLINE",
        "variation": "supported",
        "evidence": "Late fee of ₹100 per day is levied for semester fee payments made after August 15th up to a maximum of 14 days.",
        "claim": "Late fee of ₹100 per day is charged for tuition payments made after August 15th.",
        "label": "ENTAILMENT",
        "is_high_impact": True
    },
    {
        "id": "SUP-07",
        "category": "DOCUMENT_REQUIREMENT",
        "variation": "supported",
        "evidence": "An FIR copy or police missing report must be uploaded when requesting a replacement degree certificate.",
        "claim": "Submitting a police report or FIR is required to obtain a replacement degree certificate.",
        "label": "ENTAILMENT",
        "is_high_impact": True
    },
    {
        "id": "SUP-08",
        "category": "ELIGIBILITY",
        "variation": "supported",
        "evidence": "Merit scholarships require a minimum cumulative grade point average (CGPA) of 8.0 with no backlogs.",
        "claim": "Eligibility for merit scholarships requires a CGPA of at least 8.0 without any backlogs.",
        "label": "ENTAILMENT",
        "is_high_impact": True
    },
    {
        "id": "SUP-09",
        "category": "POLICY_RULE",
        "variation": "supported",
        "evidence": "Hostel room changes are permitted only during the first two weeks of the autumn semester.",
        "claim": "Hostel room transfers are only allowed during the first two weeks of the autumn semester.",
        "label": "ENTAILMENT",
        "is_high_impact": False
    },
    {
        "id": "SUP-10",
        "category": "EXCEPTION",
        "variation": "supported",
        "evidence": "Medical exemptions for attendance shortage up to 10% may be granted by the Dean Academic upon submission of hospital records within 5 days.",
        "claim": "Dean Academic may grant an attendance medical exemption up to 10% if hospital records are submitted within 5 days.",
        "label": "ENTAILMENT",
        "is_high_impact": True
    },
    {
        "id": "SUP-11",
        "category": "CONTACT",
        "variation": "supported",
        "evidence": "Inquiries regarding scholarship disbursements should be directed to the Financial Aid Helpdesk at Block 30 Room 102.",
        "claim": "The Financial Aid Helpdesk is located at Block 30 Room 102 for scholarship disbursement inquiries.",
        "label": "ENTAILMENT",
        "is_high_impact": False
    },
    {
        "id": "SUP-12",
        "category": "PROCESS",
        "variation": "supported",
        "evidence": "Grade transcripts require 5 business days for official verification and stamp by the Registrar.",
        "claim": "Official verification and stamping of grade transcripts takes 5 business days.",
        "label": "ENTAILMENT",
        "is_high_impact": False
    },
    {
        "id": "SUP-13",
        "category": "POLICY_RULE",
        "variation": "supported",
        "evidence": "Possession of electronic gadgets inside the examination hall constitutes an automatic Level 2 Unfair Means Case (UMC).",
        "claim": "Carrying electronic gadgets into the exam hall leads to a Level 2 UMC charge.",
        "label": "ENTAILMENT",
        "is_high_impact": True
    },

    # -------------------------------------------------------------
    # 2. Contradicted Claims (Direct Contradiction)
    # -------------------------------------------------------------
    {
        "id": "CON-01",
        "category": "FEE",
        "variation": "contradiction",
        "evidence": "Examination re-evaluation and scrutiny fees are strictly non-refundable under any circumstances.",
        "claim": "Re-evaluation fees will be refunded if the student's grade changes.",
        "label": "CONTRADICTION",
        "is_high_impact": True
    },
    {
        "id": "CON-02",
        "category": "POLICY_RULE",
        "variation": "contradiction",
        "evidence": "Students with less than 65% attendance are completely debarred and ineligible for any condonation.",
        "claim": "Students with less than 65% attendance can still receive an attendance waiver from their HOD.",
        "label": "CONTRADICTION",
        "is_high_impact": True
    },
    {
        "id": "CON-03",
        "category": "ELIGIBILITY",
        "variation": "contradiction",
        "evidence": "Only undergraduate students in semester 4 and above are eligible to apply for industry internships.",
        "claim": "All undergraduate students from semester 1 onwards are eligible for industry internships.",
        "label": "CONTRADICTION",
        "is_high_impact": True
    },
    {
        "id": "CON-04",
        "category": "POLICY_RULE",
        "variation": "contradiction",
        "evidence": "All campus hostel gates close promptly at 10:00 PM without exception.",
        "claim": "Hostel gates remain open until midnight on weekends.",
        "label": "CONTRADICTION",
        "is_high_impact": False
    },
    {
        "id": "CON-05",
        "category": "PROCESS",
        "variation": "contradiction",
        "evidence": "No physical paper applications for re-evaluation are accepted; all submissions must be made through UMS online.",
        "claim": "Students must submit hard copy re-evaluation forms to the examination counter.",
        "label": "CONTRADICTION",
        "is_high_impact": False
    },
    {
        "id": "CON-06",
        "category": "FEE",
        "variation": "contradiction",
        "evidence": "Late submission of semester course registration carries a mandatory penalty of ₹500.",
        "claim": "There is no late fee or penalty for delayed semester course registration.",
        "label": "CONTRADICTION",
        "is_high_impact": True
    },
    {
        "id": "CON-07",
        "category": "ELIGIBILITY",
        "variation": "contradiction",
        "evidence": "Students with pending disciplinary inquiries are strictly barred from participating in campus placement drives.",
        "claim": "Students under active disciplinary inquiry can freely register for campus placements.",
        "label": "CONTRADICTION",
        "is_high_impact": True
    },
    {
        "id": "CON-08",
        "category": "EXCEPTION",
        "variation": "contradiction",
        "evidence": "No grace marks shall be awarded for practical laboratory examinations.",
        "claim": "Students can receive up to 5 grace marks in practical laboratory examinations.",
        "label": "CONTRADICTION",
        "is_high_impact": True
    },
    {
        "id": "CON-09",
        "category": "DEADLINE",
        "variation": "contradiction",
        "evidence": "Hostel mess rebate applications must be submitted 3 days prior to departure.",
        "claim": "Mess rebate claims can be submitted after returning from leave.",
        "label": "CONTRADICTION",
        "is_high_impact": False
    },
    {
        "id": "CON-10",
        "category": "DOCUMENT_REQUIREMENT",
        "variation": "contradiction",
        "evidence": "Original medical certificates from a registered practitioner must be submitted in person.",
        "claim": "Photocopies of medical slips sent via WhatsApp are officially accepted.",
        "label": "CONTRADICTION",
        "is_high_impact": True
    },

    # -------------------------------------------------------------
    # 3. Neutral Claims (Informational / Unrelated Premise)
    # -------------------------------------------------------------
    {
        "id": "NEU-01",
        "category": "GENERAL_INFORMATION",
        "variation": "neutral",
        "evidence": "Students seeking end-term re-evaluation must submit their application within 7 calendar days of result declaration.",
        "claim": "The university library is open 24 hours during end-term examinations.",
        "label": "NEUTRAL",
        "is_high_impact": False
    },
    {
        "id": "NEU-02",
        "category": "PROCESS",
        "variation": "neutral",
        "evidence": "Tuition fees can be paid via credit card, net banking, or UPI on the student account portal.",
        "claim": "The university plans to introduce cryptocurrency payments next academic year.",
        "label": "NEUTRAL",
        "is_high_impact": False
    },
    {
        "id": "NEU-03",
        "category": "CONTACT",
        "variation": "neutral",
        "evidence": "The Chief Warden office is situated on the ground floor of Block 28.",
        "claim": "The Chief Warden previously served as Dean of Mechanical Engineering.",
        "label": "NEUTRAL",
        "is_high_impact": False
    },
    {
        "id": "NEU-04",
        "category": "ELIGIBILITY",
        "variation": "neutral",
        "evidence": "Minimum passing marks in each end-term theoretical examination is 40%.",
        "claim": "Theoretical examinations are conducted in the central indoor stadium.",
        "label": "NEUTRAL",
        "is_high_impact": False
    },
    {
        "id": "NEU-05",
        "category": "POLICY_RULE",
        "variation": "neutral",
        "evidence": "Smoking and consumption of alcohol anywhere on university campus grounds is strictly prohibited.",
        "claim": "Campus cafeterias offer tea, coffee, and fruit juices until 11 PM.",
        "label": "NEUTRAL",
        "is_high_impact": False
    },
    {
        "id": "NEU-06",
        "category": "DOCUMENT_REQUIREMENT",
        "variation": "neutral",
        "evidence": "Graduating students must submit a no-dues clearance certificate from their respective department head.",
        "claim": "Graduation day robes must be rented from the alumni center.",
        "label": "NEUTRAL",
        "is_high_impact": False
    },
    {
        "id": "NEU-07",
        "category": "FEE",
        "variation": "neutral",
        "evidence": "Hostel security deposit of ₹5,000 is refundable upon final clearance at graduation.",
        "claim": "Hostel rooms are repainted every two academic years.",
        "label": "NEUTRAL",
        "is_high_impact": False
    },
    {
        "id": "NEU-08",
        "category": "DEADLINE",
        "variation": "neutral",
        "evidence": "Course drop requests must be submitted within the first 10 days of classes.",
        "claim": "Class lectures will also be recorded and posted on the intranet.",
        "label": "NEUTRAL",
        "is_high_impact": False
    },
    {
        "id": "NEU-09",
        "category": "EXCEPTION",
        "variation": "neutral",
        "evidence": "Sports council athletes representing the university in national games receive duty leave credits.",
        "claim": "The university badminton team won three gold medals last semester.",
        "label": "NEUTRAL",
        "is_high_impact": False
    },
    {
        "id": "NEU-10",
        "category": "PROCESS",
        "variation": "neutral",
        "evidence": "WiFi registration requires submitting the MAC address of student laptops to ICT cell.",
        "claim": "The campus fiber network provides 1 Gbps internet speeds.",
        "label": "NEUTRAL",
        "is_high_impact": False
    },

    # -------------------------------------------------------------
    # 4. Paraphrases (Entailment)
    # -------------------------------------------------------------
    {
        "id": "PAR-01",
        "category": "ELIGIBILITY",
        "variation": "paraphrase",
        "evidence": "To qualify for the Dean's Honor Roll, a candidate must secure a SGPA of 9.0 or higher.",
        "claim": "Achieving a semester GPA of at least 9.0 is necessary to be placed on the Dean's Honor Roll.",
        "label": "ENTAILMENT",
        "is_high_impact": True
    },
    {
        "id": "PAR-02",
        "category": "DEADLINE",
        "variation": "paraphrase",
        "evidence": "All library books borrowed by students must be returned prior to the commencement of end-term exams.",
        "claim": "Students are required to hand back borrowed library volumes before final exams begin.",
        "label": "ENTAILMENT",
        "is_high_impact": False
    },
    {
        "id": "PAR-03",
        "category": "FEE",
        "variation": "paraphrase",
        "evidence": "An administrative charge of ₹1,000 is levied for issuing a duplicate degree certificate.",
        "claim": "Obtaining a second copy of an official degree certificate requires payment of a ₹1,000 fee.",
        "label": "ENTAILMENT",
        "is_high_impact": True
    },
    {
        "id": "PAR-04",
        "category": "POLICY_RULE",
        "variation": "paraphrase",
        "evidence": "Wearing student identification cards visibly around the neck is compulsory while on campus premises.",
        "claim": "Displaying student ID cards is mandatory for everyone on university property.",
        "label": "ENTAILMENT",
        "is_high_impact": False
    },
    {
        "id": "PAR-05",
        "category": "PROCESS",
        "variation": "paraphrase",
        "evidence": "Bus pass applications are processed exclusively through the transport portal with digital fee payment.",
        "claim": "Students must utilize the online transport system to submit applications and fees for university bus passes.",
        "label": "ENTAILMENT",
        "is_high_impact": False
    },
    {
        "id": "PAR-06",
        "category": "DOCUMENT_REQUIREMENT",
        "variation": "paraphrase",
        "evidence": "Students requesting medical leaves extending beyond 3 days must furnish a prescription along with a diagnosis certificate.",
        "claim": "Medical absences exceeding 3 days require a doctor's diagnosis certificate and prescription.",
        "label": "ENTAILMENT",
        "is_high_impact": True
    },
    {
        "id": "PAR-07",
        "category": "EXCEPTION",
        "variation": "paraphrase",
        "evidence": "Special consideration for late submission of capstone projects is granted only under catastrophic medical distress.",
        "claim": "Severe health emergencies are the sole accepted grounds for late submission of final capstone work.",
        "label": "ENTAILMENT",
        "is_high_impact": True
    },
    {
        "id": "PAR-08",
        "category": "CONTACT",
        "variation": "paraphrase",
        "evidence": "For grievance redressal, email the student ombudsman at ombudsman@university.edu.in.",
        "claim": "Students may submit official grievances to the university ombudsman via ombudsman@university.edu.in.",
        "label": "ENTAILMENT",
        "is_high_impact": False
    },
    {
        "id": "PAR-09",
        "category": "POLICY_RULE",
        "variation": "paraphrase",
        "evidence": "Ragging in any form is a zero-tolerance criminal offense punishable by immediate rustication.",
        "claim": "The university enforces zero tolerance for ragging and expels offenders immediately.",
        "label": "ENTAILMENT",
        "is_high_impact": True
    },
    {
        "id": "PAR-10",
        "category": "DEADLINE",
        "variation": "paraphrase",
        "evidence": "Semester registration without late fee closes at 5:00 PM on July 31st.",
        "claim": "Students have until 5:00 PM on July 31st to complete regular semester registration without penalty.",
        "label": "ENTAILMENT",
        "is_high_impact": True
    },

    # -------------------------------------------------------------
    # 5. Numeric Changes (Contradiction)
    # -------------------------------------------------------------
    {
        "id": "NUM-01",
        "category": "ELIGIBILITY",
        "variation": "numeric_change",
        "evidence": "Students must achieve at least 75% attendance to qualify for writing end-term exams.",
        "claim": "Students must achieve at least 85% attendance to qualify for writing end-term exams.",
        "label": "CONTRADICTION",
        "is_high_impact": True
    },
    {
        "id": "NUM-02",
        "category": "POLICY_RULE",
        "variation": "numeric_change",
        "evidence": "A student may carry forward a maximum of 2 backlogs into the final academic year.",
        "claim": "Students are permitted to carry up to 5 backlogs into their final academic year.",
        "label": "CONTRADICTION",
        "is_high_impact": True
    },
    {
        "id": "NUM-03",
        "category": "ELIGIBILITY",
        "variation": "numeric_change",
        "evidence": "A minimum CGPA of 6.0 is required for graduation degree award.",
        "claim": "A minimum CGPA of 5.0 is required for graduation degree award.",
        "label": "CONTRADICTION",
        "is_high_impact": True
    },
    {
        "id": "NUM-04",
        "category": "DEADLINE",
        "variation": "numeric_change",
        "evidence": "Students can borrow up to 4 books from the university library for 14 days.",
        "claim": "Students can borrow up to 8 books from the university library for 14 days.",
        "label": "CONTRADICTION",
        "is_high_impact": False
    },
    {
        "id": "NUM-05",
        "category": "POLICY_RULE",
        "variation": "numeric_change",
        "evidence": "The pass percentage in internal continuous assessment is 30% of total assigned marks.",
        "claim": "Internal continuous assessment requires a passing score of 50%.",
        "label": "CONTRADICTION",
        "is_high_impact": True
    },
    {
        "id": "NUM-06",
        "category": "ELIGIBILITY",
        "variation": "numeric_change",
        "evidence": "Students must complete 160 total academic credits to earn a Bachelor of Technology degree.",
        "claim": "Earning a Bachelor of Technology degree requires 120 total academic credits.",
        "label": "CONTRADICTION",
        "is_high_impact": True
    },
    {
        "id": "NUM-07",
        "category": "DEADLINE",
        "variation": "numeric_change",
        "evidence": "Leave of absence without academic penalty cannot exceed 2 consecutive semesters.",
        "claim": "Students may take up to 4 consecutive semesters of leave without penalty.",
        "label": "CONTRADICTION",
        "is_high_impact": True
    },
    {
        "id": "NUM-08",
        "category": "POLICY_RULE",
        "variation": "numeric_change",
        "evidence": "Mid-term examinations contribute 25% weightage toward the final course grade.",
        "claim": "Mid-term examinations carry 40% weightage toward the final course grade.",
        "label": "CONTRADICTION",
        "is_high_impact": True
    },
    {
        "id": "NUM-09",
        "category": "DEADLINE",
        "variation": "numeric_change",
        "evidence": "Mess rebate applies for continuous absence of at least 7 days.",
        "claim": "Mess rebate is granted for any absence of at least 3 days.",
        "label": "CONTRADICTION",
        "is_high_impact": False
    },
    {
        "id": "NUM-10",
        "category": "FEE",
        "variation": "numeric_change",
        "evidence": "Hostel room electric heater permits incur a seasonal surcharge of ₹1,200.",
        "claim": "Using an electric room heater requires a fee of ₹3,000.",
        "label": "CONTRADICTION",
        "is_high_impact": True
    },

    # -------------------------------------------------------------
    # 6. Deadline Changes (Contradiction)
    # -------------------------------------------------------------
    {
        "id": "DED-01",
        "category": "DEADLINE",
        "variation": "deadline_change",
        "evidence": "Re-evaluation applications must be submitted within 7 calendar days of result announcement.",
        "claim": "Applications for re-evaluation can be submitted within 30 days of result announcement.",
        "label": "CONTRADICTION",
        "is_high_impact": True
    },
    {
        "id": "DED-02",
        "category": "DEADLINE",
        "variation": "deadline_change",
        "evidence": "Hostel dues must be cleared within 10 days of semester commencement.",
        "claim": "Hostel dues must be cleared within 45 days of semester commencement.",
        "label": "CONTRADICTION",
        "is_high_impact": True
    },
    {
        "id": "DED-03",
        "category": "DEADLINE",
        "variation": "deadline_change",
        "evidence": "Medical certificate submission deadline is within 3 working days of resumption of classes.",
        "claim": "Students have 14 working days after returning to submit medical certificates.",
        "label": "CONTRADICTION",
        "is_high_impact": True
    },
    {
        "id": "DED-04",
        "category": "DEADLINE",
        "variation": "deadline_change",
        "evidence": "Grade dispute tickets must be registered within 48 hours of grade publication.",
        "claim": "Grade disputes can be registered anytime within 15 days of publication.",
        "label": "CONTRADICTION",
        "is_high_impact": True
    },
    {
        "id": "DED-05",
        "category": "DEADLINE",
        "variation": "deadline_change",
        "evidence": "Course withdrawal without academic penalty is permitted up to 14 days before end-term exams.",
        "claim": "Students can withdraw from a course up to 2 days before end-term exams.",
        "label": "CONTRADICTION",
        "is_high_impact": True
    },
    {
        "id": "DED-06",
        "category": "DEADLINE",
        "variation": "deadline_change",
        "evidence": "Refund claims for security deposits must be submitted within 6 months of program completion.",
        "claim": "Security deposit refunds can be claimed up to 2 years after program completion.",
        "label": "CONTRADICTION",
        "is_high_impact": True
    },
    {
        "id": "DED-07",
        "category": "DEADLINE",
        "variation": "deadline_change",
        "evidence": "Hall ticket discrepancy corrections must be reported at least 24 hours prior to examination.",
        "claim": "Corrections to hall tickets may be submitted up to 1 hour prior to examination.",
        "label": "CONTRADICTION",
        "is_high_impact": True
    },
    {
        "id": "DED-08",
        "category": "DEADLINE",
        "variation": "deadline_change",
        "evidence": "Late library return fines accrue after a grace period of 2 days.",
        "claim": "Late library fines only start accumulating after a 10 day grace period.",
        "label": "CONTRADICTION",
        "is_high_impact": False
    },
    {
        "id": "DED-09",
        "category": "DEADLINE",
        "variation": "deadline_change",
        "evidence": "Appeals against UMC committee sanctions must be filed within 5 working days.",
        "claim": "UMC sanction appeals can be submitted within 30 working days.",
        "label": "CONTRADICTION",
        "is_high_impact": True
    },
    {
        "id": "DED-10",
        "category": "DEADLINE",
        "variation": "deadline_change",
        "evidence": "Hostel room vacation notice must be provided 15 days in advance of departure.",
        "claim": "Hostel rooms can be vacated immediately with only 24 hours prior notice.",
        "label": "CONTRADICTION",
        "is_high_impact": False
    },

    # -------------------------------------------------------------
    # 7. Eligibility Changes (Contradiction)
    # -------------------------------------------------------------
    {
        "id": "ELI-01",
        "category": "ELIGIBILITY",
        "variation": "eligibility_change",
        "evidence": "Only students in semester 4 and above with no active backlogs are eligible for study abroad exchange.",
        "claim": "All students from any semester are eligible to apply for study abroad exchange.",
        "label": "CONTRADICTION",
        "is_high_impact": True
    },
    {
        "id": "ELI-02",
        "category": "ELIGIBILITY",
        "variation": "eligibility_change",
        "evidence": "Honors degree option requires maintaining a minimum CGPA of 8.5 with zero course repetitions.",
        "claim": "Any student with a CGPA above 6.5 can opt for an Honors degree.",
        "label": "CONTRADICTION",
        "is_high_impact": True
    },
    {
        "id": "ELI-03",
        "category": "ELIGIBILITY",
        "variation": "eligibility_change",
        "evidence": "Single occupancy hostel rooms are reserved exclusively for final year PhD and postgraduate scholars.",
        "claim": "First year undergraduate students are eligible to book single occupancy hostel rooms.",
        "label": "CONTRADICTION",
        "is_high_impact": False
    },
    {
        "id": "ELI-04",
        "category": "ELIGIBILITY",
        "variation": "eligibility_change",
        "evidence": "Teaching assistantships are offered only to full-time master's students with first-class graduation.",
        "claim": "Undergraduate sophomores can receive university teaching assistantships.",
        "label": "CONTRADICTION",
        "is_high_impact": True
    },
    {
        "id": "ELI-05",
        "category": "ELIGIBILITY",
        "variation": "eligibility_change",
        "evidence": "Fee concessions under sports quota are applicable only to athletes who won state or national medals.",
        "claim": "All participants in inter-hostel friendly sports events receive sports fee concessions.",
        "label": "CONTRADICTION",
        "is_high_impact": True
    },
    {
        "id": "ELI-06",
        "category": "ELIGIBILITY",
        "variation": "eligibility_change",
        "evidence": "Remedial crash courses are mandatory for students scoring less than 35% in mid-term evaluations.",
        "claim": "Remedial courses are optional and restricted to final-year students only.",
        "label": "CONTRADICTION",
        "is_high_impact": True
    },
    {
        "id": "ELI-07",
        "category": "ELIGIBILITY",
        "variation": "eligibility_change",
        "evidence": "Special re-appear examinations in the summer term are open only to graduating batch students with 1 backlog.",
        "claim": "Summer re-appear examinations are open to students of all semesters regardless of backlog count.",
        "label": "CONTRADICTION",
        "is_high_impact": True
    },
    {
        "id": "ELI-08",
        "category": "ELIGIBILITY",
        "variation": "eligibility_change",
        "evidence": "University parking permits for four-wheelers are issued only to day-scholar commuters residing beyond 15 km.",
        "claim": "All on-campus hostel residents are permitted to keep four-wheelers with parking permits.",
        "label": "CONTRADICTION",
        "is_high_impact": False
    },
    {
        "id": "ELI-09",
        "category": "ELIGIBILITY",
        "variation": "eligibility_change",
        "evidence": "Merit-cum-means financial aid is restricted to students with family annual income below ₹5,00,000.",
        "claim": "Merit-cum-means financial aid has no family income cap.",
        "label": "CONTRADICTION",
        "is_high_impact": True
    },
    {
        "id": "ELI-10",
        "category": "ELIGIBILITY",
        "variation": "eligibility_change",
        "evidence": "Only students without disciplinary warnings are eligible to run for Student Council executive posts.",
        "claim": "Students with active disciplinary reprimands are permitted to contest Student Council elections.",
        "label": "CONTRADICTION",
        "is_high_impact": True
    },

    # -------------------------------------------------------------
    # 8. Fee Changes (Contradiction)
    # -------------------------------------------------------------
    {
        "id": "FEE-01",
        "category": "FEE",
        "variation": "fee_change",
        "evidence": "End-term theory re-evaluation fee is ₹500 per subject.",
        "claim": "The fee for end-term re-evaluation is ₹5,000 per subject.",
        "label": "CONTRADICTION",
        "is_high_impact": True
    },
    {
        "id": "FEE-02",
        "category": "FEE",
        "variation": "fee_change",
        "evidence": "Late submission of hostel enrollment form incurs a fine of ₹200.",
        "claim": "Hostel enrollment late submission carries a fine of ₹2,000.",
        "label": "CONTRADICTION",
        "is_high_impact": True
    },
    {
        "id": "FEE-03",
        "category": "FEE",
        "variation": "fee_change",
        "evidence": "Official transcript fee is ₹250 for domestic delivery.",
        "claim": "Official transcript fee is ₹1,500 for domestic delivery.",
        "label": "CONTRADICTION",
        "is_high_impact": True
    },
    {
        "id": "FEE-04",
        "category": "FEE",
        "variation": "fee_change",
        "evidence": "Re-admission fee following temporary withdrawal is ₹1,000.",
        "claim": "Re-admission fee is ₹10,000 following temporary withdrawal.",
        "label": "CONTRADICTION",
        "is_high_impact": True
    },
    {
        "id": "FEE-05",
        "category": "FEE",
        "variation": "fee_change",
        "evidence": "Replacement of damaged laboratory equipment is charged at actual component cost plus ₹150 handling fee.",
        "claim": "Laboratory equipment damage carries a flat ₹5,000 penalty regardless of cost.",
        "label": "CONTRADICTION",
        "is_high_impact": True
    },
    {
        "id": "FEE-06",
        "category": "FEE",
        "variation": "fee_change",
        "evidence": "University bus transportation fee is ₹8,000 per semester for city routes.",
        "claim": "University bus fee is ₹25,000 per semester for city routes.",
        "label": "CONTRADICTION",
        "is_high_impact": True
    },
    {
        "id": "FEE-07",
        "category": "FEE",
        "variation": "fee_change",
        "evidence": "Course add-drop after standard deadline requires payment of ₹300 administrative fee.",
        "claim": "Late course adjustments carry an administrative charge of ₹3,000.",
        "label": "CONTRADICTION",
        "is_high_impact": True
    },
    {
        "id": "FEE-08",
        "category": "FEE",
        "variation": "fee_change",
        "evidence": "Lost library book replacement fee is the book price plus ₹100 cataloging surcharge.",
        "claim": "Losing a library book requires paying double the price plus a ₹1,000 penalty.",
        "label": "CONTRADICTION",
        "is_high_impact": False
    },
    {
        "id": "FEE-09",
        "category": "FEE",
        "variation": "fee_change",
        "evidence": "Migration certificate issuance charge is ₹400.",
        "claim": "Issuance of migration certificate costs ₹4,000.",
        "label": "CONTRADICTION",
        "is_high_impact": True
    },
    {
        "id": "FEE-10",
        "category": "FEE",
        "variation": "fee_change",
        "evidence": "Convocation registration fee including ceremonial robe deposit is ₹1,500.",
        "claim": "Convocation registration requires a payment of ₹6,500.",
        "label": "CONTRADICTION",
        "is_high_impact": True
    },

    # -------------------------------------------------------------
    # 9. Exception Changes (Contradiction / Neutral)
    # -------------------------------------------------------------
    {
        "id": "EXC-01",
        "category": "EXCEPTION",
        "variation": "exception_change",
        "evidence": "No exceptions to the 75% attendance rule are permitted except for documented medical hospitalization.",
        "claim": "Family vacations and personal travel are approved reasons for attendance exemption.",
        "label": "CONTRADICTION",
        "is_high_impact": True
    },
    {
        "id": "EXC-02",
        "category": "EXCEPTION",
        "variation": "exception_change",
        "evidence": "Late fee waivers are exclusively sanctioned by the Finance Officer in cases of banking system outages.",
        "claim": "Hostel wardens can arbitrarily waive tuition late fees.",
        "label": "CONTRADICTION",
        "is_high_impact": True
    },
    {
        "id": "EXC-03",
        "category": "EXCEPTION",
        "variation": "exception_change",
        "evidence": "Exemption from compulsory on-campus hostel residency is granted only to students residing with parents within 25 km.",
        "claim": "Any student can move out to private flats without parental residency verification.",
        "label": "CONTRADICTION",
        "is_high_impact": True
    },
    {
        "id": "EXC-04",
        "category": "EXCEPTION",
        "variation": "exception_change",
        "evidence": "Special examination arrangements for differently-abled students include 20 minutes extra time per hour.",
        "claim": "Differently-abled students receive 2 hours extra time per exam paper.",
        "label": "CONTRADICTION",
        "is_high_impact": True
    },
    {
        "id": "EXC-05",
        "category": "EXCEPTION",
        "variation": "exception_change",
        "evidence": "Prerequisite course waivers may only be authorized by the Academic Council.",
        "claim": "Course prerequisites can be waived by student course peers.",
        "label": "CONTRADICTION",
        "is_high_impact": True
    },
    {
        "id": "EXC-06",
        "category": "EXCEPTION",
        "variation": "exception_change",
        "evidence": "Exemption from sports curriculum is granted solely to students with permanent physical disability certificates.",
        "claim": "Students feeling tired can claim permanent sports curriculum exemption.",
        "label": "CONTRADICTION",
        "is_high_impact": False
    },
    {
        "id": "EXC-07",
        "category": "EXCEPTION",
        "variation": "exception_change",
        "evidence": "Postponement of final project viva is allowed only in case of direct bereavement in the immediate family.",
        "claim": "Project viva can be postponed for attending friends' social celebrations.",
        "label": "CONTRADICTION",
        "is_high_impact": True
    },
    {
        "id": "EXC-08",
        "category": "EXCEPTION",
        "variation": "exception_change",
        "evidence": "Late course registration without penalty is allowed if admission was offered in the final mop-up counseling round.",
        "claim": "All students can register late without penalty regardless of admission round.",
        "label": "CONTRADICTION",
        "is_high_impact": True
    },
    {
        "id": "EXC-09",
        "category": "EXCEPTION",
        "variation": "exception_change",
        "evidence": "Hostel room transfer exemptions are strictly prohibited after the initial two-week adjustment window.",
        "claim": "Students can swap hostel rooms anytime throughout the academic semester.",
        "label": "CONTRADICTION",
        "is_high_impact": False
    },
    {
        "id": "EXC-10",
        "category": "EXCEPTION",
        "variation": "exception_change",
        "evidence": "Overload course credits beyond 28 credits per semester are allowed only for students with CGPA above 9.0.",
        "claim": "Any student regardless of CGPA can register for up to 36 credits.",
        "label": "CONTRADICTION",
        "is_high_impact": True
    },

    # -------------------------------------------------------------
    # 10. Irrelevant Evidence (Neutral / Insufficient Evidence)
    # -------------------------------------------------------------
    {
        "id": "IRR-01",
        "category": "DEADLINE",
        "variation": "irrelevant_evidence",
        "evidence": "Hostel laundry services are open Monday to Friday between 8:00 AM and 6:00 PM.",
        "claim": "Re-evaluation applications must be submitted within 7 calendar days of result declaration.",
        "label": "NEUTRAL",
        "is_high_impact": True
    },
    {
        "id": "IRR-02",
        "category": "FEE",
        "variation": "irrelevant_evidence",
        "evidence": "The campus central cafeteria accepts digital payment cards and campus wallet.",
        "claim": "End-term re-evaluation fee is ₹500 per theory subject.",
        "label": "NEUTRAL",
        "is_high_impact": True
    },
    {
        "id": "IRR-03",
        "category": "ELIGIBILITY",
        "variation": "irrelevant_evidence",
        "evidence": "Visitor parking is allocated near Gate 1 upon security gate pass registration.",
        "claim": "A minimum of 75% attendance is required to be eligible for final examinations.",
        "label": "NEUTRAL",
        "is_high_impact": True
    },
    {
        "id": "IRR-04",
        "category": "PROCESS",
        "variation": "irrelevant_evidence",
        "evidence": "University gym equipment must be wiped down after use by each member.",
        "claim": "Students can apply for duplicate ID cards through the student portal.",
        "label": "NEUTRAL",
        "is_high_impact": False
    },
    {
        "id": "IRR-05",
        "category": "DOCUMENT_REQUIREMENT",
        "variation": "irrelevant_evidence",
        "evidence": "Hostel mess menus are revised bi-monthly by the Student Mess Committee.",
        "claim": "A police FIR copy is required when applying for a duplicate degree.",
        "label": "NEUTRAL",
        "is_high_impact": True
    },
    {
        "id": "IRR-06",
        "category": "CONTACT",
        "variation": "irrelevant_evidence",
        "evidence": "Campus shuttle buses operate on a 15-minute frequency between residential blocks and academic wings.",
        "claim": "Contact the Chief Warden office at Block 28 Room 101 for room reallocation.",
        "label": "NEUTRAL",
        "is_high_impact": False
    },
    {
        "id": "IRR-07",
        "category": "POLICY_RULE",
        "variation": "irrelevant_evidence",
        "evidence": "Bicycles must be locked in designated stands outside academic buildings.",
        "claim": "Possession of electronic gadgets in exam halls leads to Level 2 UMC charges.",
        "label": "NEUTRAL",
        "is_high_impact": True
    },
    {
        "id": "IRR-08",
        "category": "EXCEPTION",
        "variation": "irrelevant_evidence",
        "evidence": "The university botanical garden is reserved for forestry research scholars on weekends.",
        "claim": "Medical attendance exemptions up to 10% may be granted by Dean Academic.",
        "label": "NEUTRAL",
        "is_high_impact": True
    },
    {
        "id": "IRR-09",
        "category": "FEE",
        "variation": "irrelevant_evidence",
        "evidence": "Swimming pool lockers require a refundable key deposit of ₹50.",
        "claim": "Semester tuition late fees accrue at ₹100 per day after the due date.",
        "label": "NEUTRAL",
        "is_high_impact": True
    },
    {
        "id": "IRR-10",
        "category": "ELIGIBILITY",
        "variation": "irrelevant_evidence",
        "evidence": "Recycling bins for paper and plastic are stationed on every departmental corridor.",
        "claim": "Merit scholarships require a minimum CGPA of 8.0 without any backlogs.",
        "label": "NEUTRAL",
        "is_high_impact": True
    },

    # -------------------------------------------------------------
    # 11. Missing Evidence (Neutral / Insufficient Evidence)
    # -------------------------------------------------------------
    {
        "id": "MIS-01",
        "category": "POLICY_RULE",
        "variation": "missing_evidence",
        "evidence": "",
        "claim": "Students are entitled to a full refund of tuition fees if they drop out within 15 days.",
        "label": "NEUTRAL",
        "is_high_impact": True
    },
    {
        "id": "MIS-02",
        "category": "DEADLINE",
        "variation": "missing_evidence",
        "evidence": "",
        "claim": "Hostel room changes must be submitted before Friday 5 PM.",
        "label": "NEUTRAL",
        "is_high_impact": False
    },
    {
        "id": "MIS-03",
        "category": "FEE",
        "variation": "missing_evidence",
        "evidence": "",
        "claim": "A special sports equipment rental fee of ₹500 per month applies.",
        "label": "NEUTRAL",
        "is_high_impact": True
    },
    {
        "id": "MIS-04",
        "category": "ELIGIBILITY",
        "variation": "missing_evidence",
        "evidence": "",
        "claim": "All international exchange students receive a free monthly stipend of ₹10,000.",
        "label": "NEUTRAL",
        "is_high_impact": True
    },
    {
        "id": "MIS-05",
        "category": "PROCESS",
        "variation": "missing_evidence",
        "evidence": "",
        "claim": "Submit your passport to counter 4 for visa endorsement.",
        "label": "NEUTRAL",
        "is_high_impact": True
    },
    {
        "id": "MIS-06",
        "category": "DOCUMENT_REQUIREMENT",
        "variation": "missing_evidence",
        "evidence": "",
        "claim": "Students must submit an affidavit signed by a first-class magistrate for name correction.",
        "label": "NEUTRAL",
        "is_high_impact": True
    },
    {
        "id": "MIS-07",
        "category": "EXCEPTION",
        "variation": "missing_evidence",
        "evidence": "",
        "claim": "Students living in off-campus apartments can claim free university mess dining.",
        "label": "NEUTRAL",
        "is_high_impact": True
    },
    {
        "id": "MIS-08",
        "category": "CONTACT",
        "variation": "missing_evidence",
        "evidence": "",
        "claim": "The university counseling helpline is available at 1800-999-000.",
        "label": "NEUTRAL",
        "is_high_impact": False
    },
    {
        "id": "MIS-09",
        "category": "POLICY_RULE",
        "variation": "missing_evidence",
        "evidence": "",
        "claim": "Graduating with distinction requires completing two foreign language electives.",
        "label": "NEUTRAL",
        "is_high_impact": True
    },
    {
        "id": "MIS-10",
        "category": "FEE",
        "variation": "missing_evidence",
        "evidence": "",
        "claim": "Convocation guest entry tickets cost ₹200 per attendee.",
        "label": "NEUTRAL",
        "is_high_impact": False
    },

    # -------------------------------------------------------------
    # 12. Ambiguous Evidence (Neutral / Insufficient Evidence)
    # -------------------------------------------------------------
    {
        "id": "AMB-01",
        "category": "FEE",
        "variation": "ambiguous_evidence",
        "evidence": "Examination processing and review fees are determined periodically by the competent university authority.",
        "claim": "The exact fee for end-term paper re-evaluation is ₹500 per course.",
        "label": "NEUTRAL",
        "is_high_impact": True
    },
    {
        "id": "AMB-02",
        "category": "DEADLINE",
        "variation": "ambiguous_evidence",
        "evidence": "All student applications should be submitted in a timely manner as notified from time to time.",
        "claim": "Re-evaluation applications must strictly be submitted within 7 calendar days.",
        "label": "NEUTRAL",
        "is_high_impact": True
    },
    {
        "id": "AMB-03",
        "category": "ELIGIBILITY",
        "variation": "ambiguous_evidence",
        "evidence": "Students are expected to attend classes regularly and meet established academic criteria.",
        "claim": "A minimum of 75% attendance across all courses is mandatory.",
        "label": "NEUTRAL",
        "is_high_impact": True
    },
    {
        "id": "AMB-04",
        "category": "POLICY_RULE",
        "variation": "ambiguous_evidence",
        "evidence": "Hostel rules regarding night curfews are enforced by wardens according to seasonal advisories.",
        "claim": "Hostel gates are locked every night at exactly 10:00 PM without exception.",
        "label": "NEUTRAL",
        "is_high_impact": False
    },
    {
        "id": "AMB-05",
        "category": "EXCEPTION",
        "variation": "ambiguous_evidence",
        "evidence": "Appropriate relaxations may be considered by university authorities under special circumstances.",
        "claim": "The Dean Academic may grant an attendance medical waiver up to 10%.",
        "label": "NEUTRAL",
        "is_high_impact": True
    },
    {
        "id": "AMB-06",
        "category": "DOCUMENT_REQUIREMENT",
        "variation": "ambiguous_evidence",
        "evidence": "Relevant identification proofs must be presented whenever requested by campus security.",
        "claim": "Displaying student RFID cards around the neck is compulsory on campus.",
        "label": "NEUTRAL",
        "is_high_impact": False
    },
    {
        "id": "AMB-07",
        "category": "PROCESS",
        "variation": "ambiguous_evidence",
        "evidence": "Students should use designated digital channels for administrative transactions.",
        "claim": "Bus pass applications are processed exclusively through the transport portal.",
        "label": "NEUTRAL",
        "is_high_impact": False
    },
    {
        "id": "AMB-08",
        "category": "FEE",
        "variation": "ambiguous_evidence",
        "evidence": "Administrative charges apply for the replacement of damaged or lost university property.",
        "claim": "Reissuing a lost RFID card incurs a replacement charge of ₹200.",
        "label": "NEUTRAL",
        "is_high_impact": True
    },
    {
        "id": "AMB-09",
        "category": "DEADLINE",
        "variation": "ambiguous_evidence",
        "evidence": "Late payments are discouraged and may attract penal interest as decided by finance.",
        "claim": "Tuition late fees accrue at ₹100 per day after August 15th.",
        "label": "NEUTRAL",
        "is_high_impact": True
    },
    {
        "id": "AMB-10",
        "category": "ELIGIBILITY",
        "variation": "ambiguous_evidence",
        "evidence": "Merit scholarships are granted to high-performing students based on semester standing.",
        "claim": "Merit scholarship requires a minimum CGPA of 8.0 with no backlogs.",
        "label": "NEUTRAL",
        "is_high_impact": True
    }
]


def expand_dataset_to_150():
    """
    Expands the foundational seed cases into >= 150 diverse, high-fidelity synthetic evaluation items.
    """
    dataset = list(RAW_CASES)
    base_count = len(dataset)

    # Systematic expansion across departments and variation archetypes
    departments = ["Examination", "Finance", "Hostel", "Academic Affairs", "Student Welfare", "Transportation", "Security"]
    
    # Generate additional supported items
    supported_templates = [
        ("The {dept} office operates Monday through Friday from 9:00 AM to 5:00 PM.",
         "The {dept} office is open on weekdays between 9:00 AM and 5:00 PM.",
         "CONTACT", False),
        ("Official {dept} certificates are issued within {days} working days after submission.",
         "Students receive their {dept} certificates within {days} working days.",
         "DEADLINE", True),
        ("A processing fee of ₹{fee} is charged for {dept} record verification.",
         "Verification of {dept} records requires a processing fee of ₹{fee}.",
         "FEE", True),
        ("Only students enrolled in {dept} programs with CGPA above {cgpa} are eligible for department honors.",
         "Eligibility for {dept} honors requires a CGPA exceeding {cgpa}.",
         "ELIGIBILITY", True),
    ]

    counter = 1
    for dept in departments:
        for tmpl_ev, tmpl_cl, cat, hi in supported_templates:
            days = 3 if dept in ["Examination", "Finance"] else 5
            fee = 350 if dept == "Examination" else 200
            cgpa = 8.5 if dept == "Academic Affairs" else 8.0
            ev = tmpl_ev.format(dept=dept, days=days, fee=fee, cgpa=cgpa)
            cl = tmpl_cl.format(dept=dept, days=days, fee=fee, cgpa=cgpa)
            dataset.append({
                "id": f"EXP-SUP-{counter:03d}",
                "category": cat,
                "variation": "supported_department",
                "evidence": ev,
                "claim": cl,
                "label": "ENTAILMENT",
                "is_high_impact": hi
            })
            counter += 1

    # Generate additional contradiction items (numeric and deadline shifts)
    contradiction_templates = [
        ("Students must clear {dept} clearance within {days} days of semester conclusion.",
         "Students can clear {dept} clearance within {fake_days} days of semester conclusion.",
         "DEADLINE", True, 7, 30),
        ("The fine for damaged {dept} equipment is ₹{fee}.",
         "The fine for damaged {dept} equipment is ₹{fake_fee}.",
         "FEE", True, 450, 4500),
        ("Minimum {dept} workshop attendance is {att}% to obtain a certificate.",
         "Minimum {dept} workshop attendance is {fake_att}% to obtain a certificate.",
         "ELIGIBILITY", True, 80, 95),
    ]

    counter = 1
    for dept in departments:
        for tmpl_ev, tmpl_cl, cat, hi, real, fake in contradiction_templates:
            ev = tmpl_ev.format(dept=dept, days=real, fee=real, att=real)
            cl = tmpl_cl.format(dept=dept, fake_days=fake, fake_fee=fake, fake_att=fake)
            dataset.append({
                "id": f"EXP-CON-{counter:03d}",
                "category": cat,
                "variation": "contradiction_department",
                "evidence": ev,
                "claim": cl,
                "label": "CONTRADICTION",
                "is_high_impact": hi
            })
            counter += 1

    # Generate additional neutral items
    neutral_templates = [
        ("The {dept} annual conference will take place in the auditorium.",
         "Students must submit paper re-evaluation forms within 7 days.",
         "POLICY_RULE", False),
        ("The {dept} student club meets every Wednesday evening.",
         "Late fee of ₹500 is charged on tuition payments.",
         "FEE", False),
    ]

    counter = 1
    for dept in departments:
        for tmpl_ev, tmpl_cl, cat, hi in neutral_templates:
            ev = tmpl_ev.format(dept=dept)
            cl = tmpl_cl.format(dept=dept)
            dataset.append({
                "id": f"EXP-NEU-{counter:03d}",
                "category": cat,
                "variation": "neutral_department",
                "evidence": ev,
                "claim": cl,
                "label": "NEUTRAL",
                "is_high_impact": hi
            })
            counter += 1

    return dataset


def main():
    dataset = expand_dataset_to_150()
    DATASET_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(DATASET_PATH, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2)

    labels = {}
    for d in dataset:
        labels[d["label"]] = labels.get(d["label"], 0) + 1

    print(f"Generated {len(dataset)} synthetic grounding evaluation samples.")
    print(f"Label distribution: {labels}")
    print(f"Dataset written to: {DATASET_PATH}")


if __name__ == "__main__":
    main()
