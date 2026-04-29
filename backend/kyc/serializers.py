from rest_framework import serializers
from .models import KYCSubmission, Document, User
import os


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'role']
class KYCSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = KYCSubmission
        fields = "__all__"
        read_only_fields = ['user']   # 👈 IMPORTANT


class DocumentSerializer(serializers.ModelSerializer):

    submission = serializers.PrimaryKeyRelatedField(
        queryset=KYCSubmission.objects.all()
    )

    def validate_file(self, value):
        ext = os.path.splitext(value.name)[1].lower()

        if ext not in ['.pdf', '.jpg', '.jpeg', '.png']:
            raise serializers.ValidationError("Only PDF, JPG, PNG allowed")

        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("File too large (max 5MB)")

        return value

    class Meta:
        model = Document
        fields = '__all__'