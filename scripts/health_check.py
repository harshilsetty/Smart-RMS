#!/usr/bin/env python3
"""
Diagnostic utility checking local Smart RMS system readiness.
"""

import sys
import urllib.request
import json

# Safe encoding on Windows PowerShell
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

HEALTH_URL = "http://localhost:8000/health"

def run_health_check():
    print("[INFO] Testing Smart RMS API connectivity...")
    try:
        req = urllib.request.Request(HEALTH_URL, headers={"User-Agent": "SmartRMS-Diagnostic/1.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                print("[OK] API is Healthy and Responsive:")
                print(f"   - Service:     {data.get('service')}")
                print(f"   - Version:     {data.get('version')}")
                print(f"   - AI Provider: {data.get('ai_provider')}")
                print(f"   - Mock Mode:   {data.get('mock_mode')}")
                print(f"   - Environment: {data.get('environment')}")
                return True
            else:
                print(f"[FAIL] Unhealthy response: HTTP {response.status}")
                return False
    except urllib.error.URLError as e:
        print(f"[WARN] Could not connect to API at {HEALTH_URL}.")
        print(f"   Reason: {e.reason}")
        print("   Tip: Ensure the backend is running with 'uvicorn app.main:app --reload --port 8000'")
        return False

if __name__ == "__main__":
    success = run_health_check()
    sys.exit(0 if success else 1)
