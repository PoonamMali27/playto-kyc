#from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from .models import KYCSubmission, Document
from .serializers import KYCSubmissionSerializer, DocumentSerializer
from .models import Document
from django.contrib.auth.models import User 
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
User = get_user_model()

@api_view(['POST'])
def upload_document(request, id):
    try:
        submission = KYCSubmission.objects.get(id=id)

        document_type = request.data.get("document_type")
        file = request.FILES.get("document")

        # File size validation (5MB limit)
        if file.size > 5 * 1024 * 1024:
            return Response({
                "error": "File too large",
                "details": "Maximum allowed size is 5MB"
            }, status=400)

        allowed_types = ["PAN", "AADHAAR", "BANK_STATEMENT"]

        if document_type not in allowed_types:
            return Response({
                "error": "Invalid document type",
                "details": "Allowed types are PAN, AADHAAR, BANK_STATEMENT"
            }, status=400)

        if not file:
            return Response({
                "error": "No file uploaded",
                "details": "Please upload a valid document file"
            }, status=400)

        if Document.objects.filter(
            submission=submission,
            document_type=document_type
        ).exists():
            return Response({
                "error": "Document already uploaded",
                "details": f"{document_type} document is already uploaded"
            }, status=400)

        filename = file.name.lower()

        expected_keywords = {
            "PAN": ["pan"],
            "AADHAAR": ["aadhaar", "aadhar"],
            "BANK_STATEMENT": ["bank", "statement"],
        }

        if not any(keyword in filename for keyword in expected_keywords[document_type]):
            return Response({
                "error": "Wrong document uploaded",
                "details": f"Please upload a valid {document_type} document"
            }, status=400)

        Document.objects.create(
            submission=submission,
            document_type=document_type,
            file=file
        )

        return Response({
            "message": "Document uploaded successfully",
            "document_type": document_type
        }, status=201)

    except KYCSubmission.DoesNotExist:
        return Response({
            "error": "Submission not found",
            "details": f"No KYC submission found with id {id}"
        }, status=404)

@api_view(['POST'])
def save_draft(request):
    try:
        user = User.objects.first()  # temporary user until auth is proper

        submission_id = request.data.get("id")

        if submission_id:
            submission = KYCSubmission.objects.get(id=submission_id, user=user)

            serializer = KYCSubmissionSerializer(
                submission,
                data=request.data,
                partial=True
            )
        else:
            serializer = KYCSubmissionSerializer(data=request.data)

        if serializer.is_valid():
            submission = serializer.save(user=user, state="draft")
            return Response(serializer.data, status=200)

        return Response(serializer.errors, status=400)

    except Exception as e:
        return Response({"error": str(e)}, status=500)
@api_view(['POST'])
def create_kyc(request):
    try:
        user = User.objects.first()  # temp hack

        serializer = KYCSubmissionSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({"error": str(e)}, status=500)


# 🔹 Get all submissions (Reviewer)
@api_view(['GET'])
def list_submissions(request):
    submissions = KYCSubmission.objects.filter(user=request.user).order_by('created_at')
    serializer = KYCSubmissionSerializer(submissions, many=True)
    return Response(serializer.data)


# 🔹 Change state (Approve/Reject/etc)
@api_view(['POST'])
def change_state(request, pk):
    try:
        submission = KYCSubmission.objects.get(id=pk)
    except KYCSubmission.DoesNotExist:
        return Response({
            "error": "Submission not found",
            "details": f"No KYC submission found with id {pk}"
        }, status=404)

    user = User.objects.filter(username="reviewer2").first()

    if not user or user.role != "reviewer":
        return Response({
            "error": "Reviewer access required"
        }, status=403)

    new_state = request.data.get("state")
    reason = request.data.get("reason", "")

    if not new_state:
        return Response({
            "error": "Missing state",
            "details": "State field is required"
        }, status=400)

    if new_state in ["rejected", "more_info_requested"] and not reason:
        return Response({
            "error": "Reason required",
            "details": "Please provide reason for rejection or more info request"
        }, status=400)

    try:
        submission.change_state(new_state)

        if new_state in ["rejected", "more_info_requested"]:
            submission.reason = reason
            submission.save()

        return Response({
            "message": "State updated successfully",
            "state": submission.state
        })
    except ValueError as e:
        return Response({
            "error": "Invalid state transition",
            "details": str(e)
        }, status=400)
@api_view(['GET'])
def get_draft(request):
    try:
        if not request.user.is_authenticated:
            return Response({
                "error": "Authentication required",
                "details": "Please login before loading draft"
            }, status=401)
        user = User.objects.first()  # temporary until auth is proper

        draft = KYCSubmission.objects.filter(
            user=request.user,
            state__in=["draft", "more_info_requested"]
        ).order_by("-updated_at").first()

        if not draft:
            return Response({"message": "No draft found"}, status=404)

        serializer = KYCSubmissionSerializer(draft)
        return Response(serializer.data, status=200)

    except Exception as e:
        return Response({"error": str(e)}, status=500)
    
@api_view(['GET'])
def reviewer_dashboard(request):
    user = User.objects.filter(username="reviewer2").first()

    if not user:
        return Response({"error": "Reviewer user not found"}, status=404)

    if user.role != "reviewer":
        return Response({"error": "Reviewer access required"}, status=403)

    now = timezone.now()

    queue = KYCSubmission.objects.filter(
        state__in=["submitted", "under_review"]
    ).order_by("created_at")

    queue_data = []

    for item in queue:
        time_in_queue = now - item.created_at
        queue_data.append({
            "id": item.id,
            "name": item.name,
            "email": item.email,
            "business_name": item.business_name,
            "business_type": item.business_type,
            "monthly_volume": item.monthly_volume,
            "state": item.state,
            "created_at": item.created_at,
            "time_in_queue_hours": round(time_in_queue.total_seconds() / 3600, 2),
            "at_risk": time_in_queue > timedelta(hours=24),
            "documents": item.documents.url if item.documents else None,
        })

    total_queue = queue.count()

    if total_queue > 0:
        avg_seconds = sum(
            [(now - item.created_at).total_seconds() for item in queue]
        ) / total_queue
        avg_time_in_queue_hours = round(avg_seconds / 3600, 2)
    else:
        avg_time_in_queue_hours = 0

    seven_days_ago = now - timedelta(days=7)

    last_7_days = KYCSubmission.objects.filter(
        updated_at__gte=seven_days_ago,
        state__in=["approved", "rejected"]
    )

    approved_count = last_7_days.filter(state="approved").count()
    total_decided = last_7_days.count()

    approval_rate = round((approved_count / total_decided) * 100, 2) if total_decided else 0

    return Response({
        "metrics": {
            "total_submissions_in_queue": total_queue,
            "average_time_in_queue_hours": avg_time_in_queue_hours,
            "approval_rate_last_7_days": approval_rate,
        },
        "queue": queue_data
    })
@api_view(['POST'])
def resubmit_kyc(request, pk):
    try:
        submission = KYCSubmission.objects.get(id=pk)

        required_docs = ["PAN", "AADHAAR", "BANK_STATEMENT"]

        uploaded_docs = Document.objects.filter(
            submission=submission
        ).values_list("document_type", flat=True)

        missing_docs = [
            doc for doc in required_docs
            if doc not in uploaded_docs
        ]

        if missing_docs:
            return Response({
                "error": "Missing required documents",
                "details": f"Please upload: {', '.join(missing_docs)}"
            }, status=400)

        submission.change_state("submitted")

        return Response({
            "message": "KYC resubmitted successfully",
            "state": submission.state
        })

    except KYCSubmission.DoesNotExist:
        return Response({"error": "Submission not found"}, status=404)

    except ValueError as e:
        return Response({"error": str(e)}, status=400)
    
@api_view(['POST'])
def merchant_signup(request):
    username = request.data.get("username")
    password = request.data.get("password")
    email = request.data.get("email")

    if not username or not password:
        return Response({
            "error": "Missing required fields",
            "details": "username and password are required"
        }, status=400)

    if User.objects.filter(username=username).exists():
        return Response({
            "error": "User already exists",
            "details": "Username is already taken"
        }, status=400)

    user = User.objects.create_user(
        username=username,
        password=password,
        email=email,
        role="merchant"
    )

    return Response({
        "message": "Merchant account created successfully",
        "user_id": user.id,
        "username": user.username,
        "role": user.role
    }, status=201)

@api_view(['GET'])
def seed_users(request):
    merchant, _ = User.objects.get_or_create(
        username="merchant1",
        defaults={
            "email": "merchant1@test.com",
            "role": "merchant",
        }
    )
    merchant.set_password("12345")
    merchant.save()

    reviewer, _ = User.objects.get_or_create(
        username="reviewer2",
        defaults={
            "email": "reviewer2@test.com",
            "role": "reviewer",
            "is_staff": True,
            "is_superuser": True,
        }
    )
    reviewer.set_password("12345")
    reviewer.role = "reviewer"
    reviewer.is_staff = True
    reviewer.is_superuser = True
    reviewer.save()

    return Response({
        "message": "Users seeded successfully",
        "merchant": merchant.username,
        "reviewer": reviewer.username
    })