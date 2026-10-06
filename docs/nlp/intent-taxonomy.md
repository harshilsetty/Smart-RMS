# Smart RMS — University RMS Intent Taxonomy

## 1. Intent Categories

The intent taxonomy covers canonical student grievances, inquiries, and service requests within the synthetic university environment:

| Intent Key | Description | Target Department | Example Keywords / Phrases |
| :--- | :--- | :--- | :--- |
| `HOSTEL_MAINTENANCE` | Room plumbing, electrical faults, air conditioner noise, furniture repair, mess hygiene. | Hostel Affairs | `leak`, `ac unit`, `geyser`, `switchboard`, `warden`, `room`, `mess` |
| `FEE_PAYMENT` | Tuition fee double deduction, payment gateway timeout, receipt not generated, excess fee refund. | Accounts & Finance | `tuition`, `fee`, `deducted twice`, `gateway`, `bank`, `refund`, `challan` |
| `EXAMINATION` | Admit card/hall ticket hold, library clearance blocker, datesheet clash, seating plan, center issues. | Examination Branch | `admit card`, `hall ticket`, `datesheet clash`, `clearance hold`, `exam center` |
| `ACADEMIC` | Continuous Assessment (CA) rubric discrepancy, marks missing, elective allotment error, syllabus query. | Academic Affairs | `ca marks`, `rubric`, `continuous assessment`, `curriculum`, `credit registration` |
| `ATTENDANCE` | Medical leave condonation, hospitalization certificate, biometric punch failure, duty leave for sports. | Student Welfare | `medical leave`, `condonation`, `hospitalization`, `dengue`, `biometric`, `75%` |
| `SCHOLARSHIP` | National Scholarship Portal (NSP) verification, Post-Matric scheme, state nodal approval, income certificate. | Scholarship Section | `scholarship`, `nsp`, `post-matric`, `institute verification`, `freeship` |
| `IT_SUPPORT` | Campus Wi-Fi MAC address limit, UMS/LMS login error, email password reset, computer lab network down. | IT Services | `wi-fi`, `wifi`, `mac address`, `fortinet`, `portal login`, `password reset` |
| `STUDENT_SERVICES` | Official Bonafide certificate, Medium of Instruction (MOI) letter, migration, duplicate ID card. | Academic Affairs | `bonafide`, `moi`, `medium of instruction`, `migration certificate`, `duplicate id` |
| `GENERAL_INQUIRY` | Out-of-scope campus inquiries (e.g. bookstore novels, gym equipment, public bus schedules). | General Admin / Academic Affairs | `novel books`, `gym racket`, `bus timings`, `campus cafeteria` |
| `UNKNOWN` | Requests with zero recognizable domain signals or unclassifiable text. | Academic Affairs / Queue | `xyz random query`, `status pending` |

---

## 2. Unknown and Ambiguity Handling

- **`UNKNOWN` Support**: When no recognizable keyword signal matches any domain category, the classifier assigns `UNKNOWN` with confidence $0.30$ and flags `is_ambiguous = True`.
- **Ambiguity Detection**: Terse, low-information queries (e.g., `"My issue is not solved"`, `"Need help with fees"`, `"Something is wrong with my exam"`) or queries where the score margin between the top two candidate intents is $<0.5$ automatically trigger `needs_clarification = True`.
- **Policy**: The system prefers explicit uncertainty over confidently wrong autonomous classifications.
