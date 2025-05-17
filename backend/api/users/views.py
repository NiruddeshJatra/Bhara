from django.shortcuts import render
from authemail.views import Signup, Login, Logout
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import CustomSignupSerializer, UserProfileSerializer, ProfileCompletionSerializer
from .models import User
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.core.cache import cache


class CustomSignup(Signup):
    serializer_class = CustomSignupSerializer


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
        cache_key = f'user_profile_{request.user.id}'
        profile_data = cache.get(cache_key)
        
        if not profile_data:
            serializer = UserProfileSerializer(request.user)
            profile_data = serializer.data
            cache.set(cache_key, profile_data, timeout=60*15)
        
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
            cache.delete(f'user_profile_{request.user.id}')
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
            cache.delete(f'user_profile_{request.user.id}')
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)