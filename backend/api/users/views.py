from django.contrib.auth import get_user_model
from authemail.views import Signup, Login, Logout
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (
    CustomSignupSerializer,
    UserProfileSerializer,
    ProfileCompletionSerializer,
)
from .models import User
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.core.cache import cache
from authemail.models import SignupCode
from ipware import get_client_ip
from .tasks import send_verification_email


class CustomSignup(Signup):
    serializer_class = CustomSignupSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get("email")
            username = serializer.validated_data.get("username")
            password = serializer.validated_data.get("password")
            marketing_consent = serializer.validated_data.get("marketing_consent")

            try:
                user = get_user_model().objects.get(email=email)
                return Response(
                    {"message": "User with this email already exists"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            except get_user_model().DoesNotExist:
                user = get_user_model().objects.create_user(
                    email=email,
                    username=username,
                    password=password,
                    marketing_consent=marketing_consent,
                )

                ip_address = get_client_ip(request)
                if ip_address is None:
                    ip_address = "0.0.0.0"

                signup_code = SignupCode.objects.create_signup_code(user, ip_address)
                send_verification_email.delay(user.id, signup_code.code)
                return Response(
                    {
                        "email": email,
                        "username": username,
                        "marketing_consent": marketing_consent,
                    },
                    status=status.HTTP_201_CREATED,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomLogin(Login):
    def post(self, request, format=None):
        response = super().post(request, format)

        if response.status_code == status.HTTP_200_OK:
            email = request.data.get("email")
            user = User.objects.get(email=email)
            refresh = RefreshToken.for_user(user)
            response.data["refresh"] = str(refresh)
            response.data["access"] = str(refresh.access_token)

        return response


class CustomLogout(Logout):
    def get(self, request, format=None):
        return super().get(request, format)

    def post(self, request, format=None):
        response = super().get(request, format)

        refresh_token = request.data.get("refresh")
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()

        return response


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cache_key = f"user_profile_{request.user.id}"
        profile_data = cache.get(cache_key)

        if not profile_data:
            serializer = UserProfileSerializer(request.user)
            profile_data = serializer.data
            cache.set(cache_key, profile_data, timeout=60 * 15)

        return Response(profile_data)

    def patch(self, request):
        serializer = UserProfileSerializer(
            request.user, data=request.data, partial=True
        )

        if serializer.is_valid():
            allowed_fields = ["phone_number", "profile_picture", "bio", "location"]
            for field in allowed_fields:
                setattr(
                    request.user,
                    field,
                    serializer.validated_data.get(field, getattr(request.user, field)),
                )

            serializer.save()
            cache.delete(f"user_profile_{request.user.id}")
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileCompletionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ProfileCompletionSerializer(
            instance=request.user,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()
            cache.delete(f"user_profile_{request.user.id}")
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
