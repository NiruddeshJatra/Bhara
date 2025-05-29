from rest_framework import serializers
from .models import User
from .validators import validate_signup_data, validate_profile_completion_data
from authemail.serializers import SignupSerializer


class CustomSignupSerializer(SignupSerializer):
    username = serializers.CharField(required=True)
    marketing_consent = serializers.BooleanField(required=False)

    def validate(self, data):
        return validate_signup_data(data)


class UserProfileSerializer(serializers.ModelSerializer):
    member_since = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "phone_number",
            "date_of_birth",
            "profile_picture",
            "bio",
            "location",
            "average_rating",
            "member_since",
            "full_name",
            "is_trusted",
        ]

        read_only_fields = [
            "id",
            "member_since",
            "username",
            "date_of_birth",
            "email",
            "full_name",
            "average_rating",
            "is_trusted",
        ]

    def get_member_since(self, obj):
        return obj.created_at.strftime("%B %Y")

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()


class ProfileCompletionSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "phone_number",
            "location",
            "date_of_birth",
            "national_id",
            "national_id_front",
            "national_id_back",
            "profile_completed",
        ]
        read_only_fields = [
            "profile_completed",
        ]

    def validate(self, data):
        return validate_profile_completion_data(data)

    def update(self, instance, validate_data):
        for attr, value in validate_data.items():
            setattr(instance, attr, value)

        instance.profile_completed = True
        instance.save()

        return instance
