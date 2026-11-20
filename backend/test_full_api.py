"""Comprehensive API test script for CivicPulse AI backend."""
import sys
import time
import json
import urllib.request
import urllib.parse
import urllib.error

BASE = "http://127.0.0.1:8000"
ADMIN_EMAIL = "admin@civicpulse.ai"
ADMIN_PASSWORD = "CivicAdmin123!"
TEST_EMAIL = f"testcitizen_{int(time.time())}@example.com"
TEST_PASSWORD = "SecurePass123"

results = []

def test(name, method, path, body=None, headers=None, expected_status=None, form_encoded=False):
    """Run a single API test and store result."""
    url = f"{BASE}{path}"
    if headers is None:
        headers = {}
    
    if body and not form_encoded:
        data = json.dumps(body).encode("utf-8")
        headers.setdefault("Content-Type", "application/json")
    elif body and form_encoded:
        data = urllib.parse.urlencode(body).encode("utf-8")
        headers.setdefault("Content-Type", "application/x-www-form-urlencoded")
    else:
        data = None

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        status_code = resp.status
        resp_body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        status_code = e.code
        try:
            resp_body = json.loads(e.read().decode("utf-8"))
        except Exception:
            resp_body = {"raw": str(e)}
    except Exception as e:
        status_code = 0
        resp_body = {"error": str(e)}

    if expected_status:
        passed = status_code == expected_status
    else:
        passed = 200 <= status_code < 300

    emoji = "PASS" if passed else "FAIL"
    results.append({"name": name, "status": emoji, "http_status": status_code})
    print(f"  [{emoji}] {name} -> HTTP {status_code}", flush=True)
    if not passed:
        print(f"        Response: {json.dumps(resp_body, indent=2)[:300]}", flush=True)
    return resp_body, status_code, passed


print("=" * 70, flush=True)
print("CivicPulse AI — Comprehensive API Test Suite", flush=True)
print("=" * 70, flush=True)

# 1. Health Check
print("\n--- Health Check ---", flush=True)
test("Health endpoint", "GET", "/api/v1/health")

# 2. Auth: Register new user
print("\n--- Authentication ---", flush=True)
reg_body, reg_status, reg_ok = test(
    "Register new citizen",
    "POST", "/api/v1/auth/register",
    body={"full_name": "Test Citizen", "email": TEST_EMAIL, "password": TEST_PASSWORD, "phone": "+919876543210"},
)

# 3. Auth: Register duplicate email
test(
    "Register duplicate email (expect 400)",
    "POST", "/api/v1/auth/register",
    body={"full_name": "Dupe", "email": TEST_EMAIL, "password": TEST_PASSWORD},
    expected_status=400,
)

# 4. Auth: Login (form-encoded) with new user
login_body, login_status, login_ok = test(
    "Login new user (form /token)",
    "POST", "/api/v1/auth/token",
    body={"username": TEST_EMAIL, "password": TEST_PASSWORD},
    form_encoded=True,
)

citizen_token = login_body.get("access_token", "") if login_ok else ""
citizen_refresh = login_body.get("refresh_token", "") if login_ok else ""

# 5. Auth: Login with wrong password
test(
    "Login wrong password (expect 401)",
    "POST", "/api/v1/auth/token",
    body={"username": TEST_EMAIL, "password": "WrongPassword1"},
    form_encoded=True,
    expected_status=401,
)

# 6. Auth: JSON login
json_login_body, _, json_login_ok = test(
    "Login new user (JSON /login)",
    "POST", "/api/v1/auth/login",
    body={"email": TEST_EMAIL, "password": TEST_PASSWORD},
)

# 7. Auth: Get current user (/me)
me_body, _, me_ok = test(
    "Get current user (/me)",
    "GET", "/api/v1/auth/me",
    headers={"Authorization": f"Bearer {citizen_token}"} if citizen_token else {},
)

# 8. Auth: Login as admin
admin_login, _, admin_ok = test(
    "Login as admin (form /token)",
    "POST", "/api/v1/auth/token",
    body={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
    form_encoded=True,
)
admin_token = admin_login.get("access_token", "") if admin_ok else ""

# 9. Auth: Refresh token
if citizen_refresh:
    test(
        "Refresh token",
        "POST", "/api/v1/auth/refresh",
        headers={"Authorization": f"Bearer {citizen_refresh}"},
    )

# 10. Complaints: Stats
print("\n--- Complaints ---", flush=True)
test("Complaint stats", "GET", "/api/v1/complaints/stats",
     headers={"Authorization": f"Bearer {citizen_token}"} if citizen_token else {})

# 11. Complaints: List (public)
test("List complaints", "GET", "/api/v1/complaints/",
     headers={"Authorization": f"Bearer {citizen_token}"} if citizen_token else {})

# 12. Complaints: Create
complaint_body, _, complaint_ok = test(
    "Create complaint",
    "POST", "/api/v1/complaints/",
    body={
        "title": "Large pothole on Main Street",
        "description": "There is a dangerous pothole on Main Street near the bus stop that has been growing larger.",
        "category": "pothole",
        "location_address": "Main Street, near Bus Stop #42, Whitefield",
        "latitude": 12.9716,
        "longitude": 77.7500,
        "ward": "Whitefield Ward 1",
    },
    headers={"Authorization": f"Bearer {citizen_token}"} if citizen_token else {},
)
complaint_id = complaint_body.get("id", "") if complaint_ok else ""

# 13. Complaints: My complaints
test("My complaints", "GET", "/api/v1/complaints/my",
     headers={"Authorization": f"Bearer {citizen_token}"} if citizen_token else {})

# 14. Complaints: Get by ID
if complaint_id:
    test("Get complaint by ID", "GET", f"/api/v1/complaints/{complaint_id}",
         headers={"Authorization": f"Bearer {citizen_token}"} if citizen_token else {})

# 15. Complaints: AI Analysis
if complaint_id:
    ai_body, _, ai_ok = test(
        "AI Analysis for complaint",
        "GET", f"/api/v1/complaints/{complaint_id}/ai-analysis",
        headers={"Authorization": f"Bearer {citizen_token}"} if citizen_token else {},
    )
    if ai_ok:
        print(f"        Impact Score: {ai_body.get('community_impact_score', {}).get('score')}", flush=True)
        print(f"        Recommended Dept: {ai_body.get('recommended_department')}", flush=True)

# 16. Complaints: Timeline
if complaint_id:
    timeline_body, _, timeline_ok = test(
        "Complaint timeline",
        "GET", f"/api/v1/complaints/{complaint_id}/timeline",
        headers={"Authorization": f"Bearer {citizen_token}"} if citizen_token else {},
    )
    if timeline_ok:
        print(f"        Timeline events: {len(timeline_body)}", flush=True)

# 17. Complaints: Update (admin status change)
if complaint_id and admin_token:
    test("Update complaint status (admin)",
         "PATCH", f"/api/v1/complaints/{complaint_id}",
         body={"status": "under_review", "assigned_to": "Inspector Ravi Kumar"},
         headers={"Authorization": f"Bearer {admin_token}"})

# 18. Departments
test("List departments", "GET", "/api/v1/complaints/departments",
     headers={"Authorization": f"Bearer {citizen_token}"} if citizen_token else {})

# 19. Create a second complaint for map/list testing
if citizen_token:
    test("Create second complaint (streetlight)",
         "POST", "/api/v1/complaints/",
         body={
             "title": "Broken streetlight on 5th Cross",
             "description": "The streetlight outside building #22 on 5th Cross has been off for over a week. Very dark and unsafe at night.",
             "category": "streetlight",
             "location_address": "5th Cross, Whitefield",
             "latitude": 12.9750,
             "longitude": 77.7520,
             "ward": "Whitefield Ward 2",
         },
         headers={"Authorization": f"Bearer {citizen_token}"})

# 20. Complaints: Filter by status
test("Filter complaints by status",
     "GET", "/api/v1/complaints/?status=submitted",
     headers={"Authorization": f"Bearer {citizen_token}"} if citizen_token else {})

# 21. Complaints: Filter by priority  
test("Filter complaints by priority",
     "GET", "/api/v1/complaints/?priority=medium",
     headers={"Authorization": f"Bearer {citizen_token}"} if citizen_token else {})

# 22. Nonexistent complaint
test("Get nonexistent complaint (expect 404)",
     "GET", "/api/v1/complaints/nonexistent-id-12345",
     headers={"Authorization": f"Bearer {citizen_token}"} if citizen_token else {},
     expected_status=404)

# 23. Unauthenticated access to protected endpoint
test("Unauthenticated /me (expect 401)",
     "GET", "/api/v1/auth/me",
     expected_status=401)

# 24. Verify admin /me
if admin_token:
    admin_me, _, admin_me_ok = test(
        "Admin /me",
        "GET", "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    if admin_me_ok:
        print(f"        Admin role: {admin_me.get('role')}", flush=True)

# Summary
print("\n" + "=" * 70, flush=True)
print("TEST SUMMARY", flush=True)
print("=" * 70, flush=True)
passed = sum(1 for r in results if r["status"] == "PASS")
failed = sum(1 for r in results if r["status"] == "FAIL")
print(f"Total: {len(results)}  |  Passed: {passed}  |  Failed: {failed}", flush=True)
print("=" * 70, flush=True)

for r in results:
    print(f"  [{r['status']}] {r['name']} (HTTP {r['http_status']})", flush=True)

sys.exit(0 if failed == 0 else 1)
