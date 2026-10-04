# Synthetic University Environment Specification

## 1. Overview & Purpose

The Synthetic University Environment provides a production-grade simulation of a large-scale university administrative ecosystem (modelled after Lovely Professional University - LPU).

### Primary Principles:
1. **Zero Real PII**: No real student names, registration numbers, phone numbers, or email addresses are stored. All identities are generated with synthetic prefixes (e.g. `STU-SYN-8492`, `REG-2023-8492`).
2. **Stable Data Contract**: Synthetic data models strictly comply with `RMSRequest`, `Department`, `StaffUser`, and `SLARecord`.
3. **Pluggable Architecture**: The mock environment acts as the active implementation of `UniversitySystemAdapter`. Swapping to staging or production involves toggling configuration to `FutureUMSAdapter` with zero alterations to core AI, RAG, or triage logic.

---

## 2. Department Taxonomy

The environment models 7 distinct university operational divisions:

| Department ID | Code | Name | Categories Handled | Default SLA (L/M/H/C) |
|---------------|------|------|--------------------|-----------------------|
| `DEPT-HOSTEL` | `HA` | Hostel Affairs | Maintenance, Mess, Room Allocation, Plumbing | 48h / 24h / 12h / 4h |
| `DEPT-ACCOUNTS` | `AF` | Accounts & Finance | Fee Payment, Refund Request, Duplicate Debits | 72h / 48h / 24h / 12h |
| `DEPT-ACADEMICS`| `AA` | Academic Affairs | CA Marks, Grade Ledger, Course Registration | 72h / 48h / 24h / 8h |
| `DEPT-EXAM` | `EB` | Examination Branch | Hall Tickets, Clearance Holds, Re-evaluation | 48h / 24h / 12h / 4h |
| `DEPT-WELFARE` | `SW` | Student Welfare | Medical Leave Condonation, Grievances | 72h / 36h / 18h / 6h |
| `DEPT-SCHOLARSHIP` | `SS` | Scholarship Section | National Scholarship Portal, Verification | 96h / 72h / 36h / 12h |
| `DEPT-IT` | `IT` | IT Services | Wi-Fi MAC Binding, UMS Credentials | 48h / 24h / 8h / 2h |

---

## 3. Synthetic Staff Roles & Workload

The environment includes realistic university staff roles:

- `STAFF_OPERATOR`: Frontline departmental desk staff handling triage, investigation, and drafting.
- `DEPARTMENT_STAFF`: Subject matter specialists processing financial reconciliations and medical validations.
- `HOD` / `DEPARTMENT_HOD`: Department Heads handling escalations, policy overrides, and emergency clearance releases.
- `ADMIN` / `SYSTEM_ADMIN`: Platform operations, audit log review, and system configuration.

Staff workloads are tracked via `WorkloadMetadata` (`assigned_tickets_count`, `open_tickets_count`, `max_capacity`).

---

## 4. REST API Endpoints for Synthetic Environment

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/rms` | `GET` | List tickets with filters (department, priority, status, search) |
| `/api/v1/rms` | `POST` | Ingest new synthetic RMS ticket |
| `/api/v1/rms/{id}` | `GET` | Retrieve complete ticket details |
| `/api/v1/rms/{id}/assign` | `POST` | Assign ticket to department/staff |
| `/api/v1/rms/{id}/responses` | `POST` | Add staff/student communication |
| `/api/v1/rms/{id}/history` | `GET` | Retrieve immutable audit history |
| `/api/v1/departments` | `GET` | List all departments and SLA policies |
| `/api/v1/departments/{id}` | `GET` | Get department details and policies |
| `/api/v1/users` | `GET` | List staff users with role/dept filtering |
| `/api/v1/users/{id}` | `GET` | Get staff user profile and workload |

---

## 5. Migration to Real University Data Sources

When approved university staging APIs become active:

```ini
# .env
INTEGRATION_MODE=ums_staging
UMS_GATEWAY_URL=https://staging.ums.university.internal/api/v2
UMS_CLIENT_ID=smart_rms_staging_client
UMS_CLIENT_SECRET=vault_secret_key
```

The factory in `RMSService` automatically switches from `MockRMSAdapter` to `FutureUMSAdapter`. Because both adapters adhere to `UniversitySystemAdapter`, no core Smart RMS code is modified.
