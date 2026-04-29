from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser


# 🔹 Custom User Model
class User(AbstractUser):
    ROLE_CHOICES = (
        ('merchant', 'Merchant'),
        ('reviewer', 'Reviewer'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)


# 🔹 KYC Submission Model
class KYCSubmission(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    STATE_CHOICES = (
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('more_info_requested', 'More Info Requested'),
    )

    # Personal Details
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)

    # Business Details
    business_name = models.CharField(max_length=100, blank=True)
    business_type = models.CharField(max_length=50, blank=True)
    monthly_volume = models.IntegerField(null=True, blank=True)
    currency = models.CharField(max_length=10, default="USD")

    documents = models.FileField(upload_to='kyc_docs/', null=True, blank=True)

    # State Machine
    state = models.CharField(max_length=30, choices=STATE_CHOICES, default='draft')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ✅ FIX: method class आत आणला
    def change_state(self, new_state):
        from .state_machine import KYCStateMachine

        KYCStateMachine.validate_transition(self.state, new_state)

        self.state = new_state
        self.save()

        Notification.objects.create(
            user=self.user,
            event_type="STATE_CHANGED",
            payload={
                "new_state": new_state,
                "submission_id": self.id
            }
        )

# 🔹 Document Model
class Document(models.Model):
    DOCUMENT_TYPES = (
        ("PAN", "PAN"),
        ("AADHAAR", "Aadhaar"),
        ("BANK_STATEMENT", "Bank Statement"),
    )

    submission = models.ForeignKey(KYCSubmission, on_delete=models.CASCADE, related_name="uploaded_documents")
    document_type = models.CharField(max_length=30, choices=DOCUMENT_TYPES)
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=50)
    payload = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)