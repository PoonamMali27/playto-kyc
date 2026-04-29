# KYC Pipeline System

A full-stack KYC (Know Your Customer) workflow system with:

- Merchant onboarding
- Document upload & validation
- Reviewer approval pipeline
- SLA tracking
- State machine enforcement
- Dockerized setup

---

# Features

## Merchant

- Signup & KYC submission
- Multi-step form
- Save Draft
- Resubmit flow
- Upload mandatory documents:
  - PAN
  - Aadhaar
  - Bank Statement

## Document Validation

- Mandatory 3 documents
- Duplicate upload prevention
- Wrong document detection (filename check)
- File size validation (max 5MB)

## Reviewer

- Dashboard with queue
- Start Review
- Approve / Reject / Request More Info
- SLA tracking (24-hour risk flag)

## State Machine

```text
draft → submitted → under_review → approved/rejected/more_info_requested
more_info_requested → submitted

 # Tech Stack

Backend:

Django
Django REST Framework

Frontend:

React (Vite)
Tailwind CSS

DevOps:

Docker
Docker Compose

# Project Structure:

playto-kyc/
├── backend/
│   ├── kyc/
│   ├── manage.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   └── kyc-frontend/
│       ├── src/
│       └── Dockerfile
│
├── docker-compose.yml
├── EXPLAINER.md
└── README.md

Setup Instructions:

 1. Clone repo

git clone <your-repo-url>
cd playto-kyc

 2. Backend Setup (without Docker)

cd backend
python -m venv venv
venv\Scripts\activate   # Windows

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

Backend runs at:

http://127.0.0.1:8000

3. Frontend Setup (without Docker)

cd frontend/kyc-frontend
npm install
npm run dev

Frontend runs at:

http://localhost:5173

Docker Setup (Recommended)

Run full project

docker-compose up --build

 Access

Service	URL

Frontend	http://localhost:5173

Backend	http://127.0.0.1:8000

Admin	http://127.0.0.1:8000/admin

Test Credentials:

Reviewer

username: reviewer2
password: 12345

Merchant

Create via signup API

 Key API Endpoints:

Merchant

Create KYC:

POST /api/v1/kyc/

Save Draft:

POST /api/v1/kyc/draft/

Get Draft:

GET /api/v1/kyc/draft/latest/

Upload Document:

POST /api/v1/upload/<id>/

Resubmit:

POST /api/v1/kyc/<id>/resubmit/

Reviewer

Dashboard:

GET /api/v1/reviewer/dashboard/

Change State:

POST /api/v1/kyc/<id>/state/

Business Logic

Mandatory Documents

PAN
Aadhaar
Bank Statement

Submission cannot be resubmitted without all 3.

File Size Limit

Max allowed: 5MB

Larger files rejected with:
{
  "error": "File too large"
}

State Transitions

Invalid transitions blocked:

submitted → rejected 

Correct flow:

submitted → under_review → rejected 

Reviewer Dashboard

Queue sorted by oldest first

SLA flag:

24 hours → At Risk

Metrics:

Total queue
Average time
Approval rate

Security

Merchant can only access their data:
KYCSubmission.objects.filter(user=request.user)
Reviewer-only actions enforced

Optional Enhancements (Future Scope)

JWT Authentication
OCR document verification
Email notifications
Async processing (Celery)
Virus scanning

Testing Flow

Merchant Flow
Fill form
Upload all 3 documents
Submit
Resubmit
Reviewer Flow
Open dashboard
Start Review
Approve / Reject / Request More Info

Key Highlights

State machine enforced at model level
Strong validation pipeline
Role-based access control
Clean frontend UX
Dockerized deployment

 Documentation

 See EXPLAINER.md for deep technical explanation