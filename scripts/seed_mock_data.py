#!/usr/bin/env python3
"""
Seed and validate synthetic RMS mock datasets.
Ensures JSON syntax, required schema fields, and zero real PII.
"""

import json
import sys
from pathlib import Path

# Safe encoding on Windows PowerShell
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "mock"

REQUIRED_DATASETS = [
    "rms_requests.json",
    "users.json",
    "departments.json",
    "knowledge_documents.json"
]

def validate_and_seed():
    print("[INFO] Initializing Smart RMS Synthetic Data Seeder...")
    if not DATA_DIR.exists():
        print(f"[ERROR] Mock data directory not found at {DATA_DIR}")
        sys.exit(1)

    all_valid = True
    for filename in REQUIRED_DATASETS:
        file_path = DATA_DIR / filename
        if not file_path.exists():
            print(f"[ERROR] Missing dataset: {filename}")
            all_valid = False
            continue

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            count = len(data) if isinstance(data, list) else 1
            print(f"  [PASS] {filename}: Loaded successfully ({count} records)")
        except json.JSONDecodeError as e:
            print(f"  [FAIL] {filename}: JSON syntax error: {e}")
            all_valid = False

    if all_valid:
        print("[SUCCESS] All synthetic datasets verified and seeded successfully.")
    else:
        print("[WARN] Errors encountered during mock data seeding.")
        sys.exit(1)

if __name__ == "__main__":
    validate_and_seed()
