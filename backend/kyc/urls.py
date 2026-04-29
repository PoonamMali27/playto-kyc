from django.urls import path
from .views import create_kyc, list_submissions, change_state, upload_document, save_draft, get_draft, reviewer_dashboard, resubmit_kyc, merchant_signup
from .views import seed_users
urlpatterns = [
    path('kyc/', create_kyc),
    path('kyc/list/', list_submissions),
    path('kyc/<int:pk>/state/', change_state),
    path('upload/<int:id>/', upload_document),
    path('kyc/draft/', save_draft),
    path('kyc/draft/latest/', get_draft),
    path('reviewer/dashboard/', reviewer_dashboard),
    path('kyc/<int:pk>/resubmit/', resubmit_kyc),
    path('auth/signup/', merchant_signup),
    path('seed-users/', seed_users),
]