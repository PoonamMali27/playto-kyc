from django.contrib import admin
from .models import User, KYCSubmission, Notification
from .models import Document

admin.site.register(User)
admin.site.register(Document)


@admin.register(KYCSubmission)
class KYCSubmissionAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "state", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "event_type", "created_at")