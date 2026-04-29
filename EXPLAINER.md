# KYC Pipeline Challenge – EXPLAINER.md

## Overview

This project implements a complete KYC workflow system with:

- Merchant KYC submission (multi-step form)
- Document upload (PAN, Aadhaar, Bank Statement)
- Strict validation (mandatory + duplicate + wrong document + file size)
- Reviewer dashboard (queue + SLA tracking)
- State machine enforcement
- Role-based access control
- Drag-and-drop upload UI
- Dockerized full-stack setup

---

# 1. THE STATE MACHINE

## Where it lives

State machine is implemented in the Django model:

```python
def change_state(self, new_state):
    allowed_transitions = {
        "draft": ["submitted"],
        "submitted": ["under_review"],
        "under_review": ["approved", "rejected", "more_info_requested"],
        "more_info_requested": ["submitted"],
    }

    if new_state not in allowed_transitions.get(self.state, []):
        raise ValueError(f"Invalid transition from {self.state} to {new_state}")

    self.state = new_state
    self.save()

How illegal transitions are prevented

Every state change must go through change_state()
Invalid transitions raise ValueError
API catches it and returns:

{
  "error": "Invalid state transition",
  "details": "Invalid transition from submitted to rejected"
}

Example

Not allowed

submitted → rejected

Correct flow

submitted → under_review → rejected

2. THE UPLOAD

Validation Code
file = request.FILES.get("document")

# File size validation (5MB)
if file.size > 5 * 1024 * 1024:
    return Response({
        "error": "File too large",
        "details": "Maximum allowed size is 5MB"
    }, status=400)

allowed_types = ["PAN", "AADHAAR", "BANK_STATEMENT"]

if document_type not in allowed_types:
    return Response({"error": "Invalid document type"}, status=400)


# Duplicate check

if Document.objects.filter(
    submission=submission,
    document_type=document_type
).exists():
    return Response({"error": "Document already uploaded"}, status=400)

# Wrong document detection

filename = file.name.lower()

expected_keywords = {
    "PAN": ["pan"],
    "AADHAAR": ["aadhaar", "aadhar"],
    "BANK_STATEMENT": ["bank", "statement"],
}

if not any(keyword in filename for keyword in expected_keywords[document_type]):
    return Response({"error": "Wrong document uploaded"}, status=400)
What happens if someone uploads a 50MB file?

Django settings allow large uploads:

DATA_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 50 * 1024 * 1024

Then application-level validation runs and rejects:

{
  "error": "File too large",
  "details": "Maximum allowed size is 5MB"
}

3. THE QUEUE

Query powering reviewer dashboard

queue = KYCSubmission.objects.filter(
    state__in=["submitted", "under_review"]
).order_by("created_at")
SLA Logic
time_in_queue = now - item.created_at

"at_risk": time_in_queue > timedelta(hours=24)
Why this design?
Filters only actionable submissions
FIFO processing using created_at
SLA calculated dynamically (no extra DB fields)

4. THE AUTH

Prevent merchant data leakage

KYCSubmission.objects.filter(user=request.user)

Result

Merchant A sees only their data
Merchant B cannot access A’s submissions

Reviewer access check

if user.role != "reviewer":
    return Response({"error": "Reviewer access required"}, status=403)
5. THE AI AUDIT
Buggy AI-generated code
await axios.post(url, {
  state: decision,  // ❌ undefined variable
});

Problem

decision was not defined
All reviewer actions failed

Fix

await axios.post(url, {
  state: state,  // ✅ correct variable
});

Learning

AI code must be reviewed
Small mistakes can break full workflow

OPTIONAL FEATURES IMPLEMENTED

Docker

Backend (Django) containerized

Frontend (React + Vite) containerized

docker-compose used

Drag-and-Drop Upload

onDrop={(e) => {
  e.preventDefault();
  setFile(e.dataTransfer.files[0]);
}}

Reviewer Dashboard

Queue list
SLA tracking

Actions:

Start Review
Approve
Reject
Request More Info

FINAL FLOW

Merchant
Fill KYC form
Upload 3 mandatory documents
Submit / Resubmit
Reviewer
Start review
Approve / Reject / Request More Info

DESIGN DECISIONS

State machine at model layer (strong consistency)
Validation at API layer
Role-based filtering for security
Simple UI navigation for demo

LIMITATIONS

Mock authentication used (no JWT/session)
No OCR verification
No async processing
No virus scanning

CONCLUSION

This system demonstrates:

Backend design (state machine, validation)
Frontend UX (multi-step form, drag-drop)
Security (data isolation)
DevOps (Docker setup)